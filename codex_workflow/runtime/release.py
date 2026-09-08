"""SemVer and verified GitHub Release acquisition for the owner's fork."""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from functools import total_ordering
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from .errors import ValidationError


RELEASES_REPOSITORY = "elmakus/codex_workflow"
RELEASES_URL = (
    f"https://api.github.com/repos/{RELEASES_REPOSITORY}/releases?per_page=100"
)
RELEASE_PAGE_SIZE = 100
MAX_METADATA_BYTES = 5 * 1024 * 1024
MAX_CHECKSUM_BYTES = 1024 * 1024
MAX_RELEASE_DOWNLOAD_BYTES = 25 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024

_GITHUB_API_HOST = "api.github.com"
_GITHUB_WEB_HOST = "github.com"
_GITHUB_DOWNLOAD_HOSTS = frozenset(
    {
        "release-assets.githubusercontent.com",
        "objects.githubusercontent.com",
        "github-releases.githubusercontent.com",
    }
)


@total_ordering
@dataclass(frozen=True)
class SemVer:
    """The precedence-bearing portion of a SemVer 2.0.0 value."""

    core: tuple[int, int, int]
    prerelease: tuple[str, ...] = ()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SemVer):
            return NotImplemented
        if self.core != other.core:
            return self.core < other.core
        if not self.prerelease:
            return False
        if not other.prerelease:
            return True
        for left, right in zip(self.prerelease, other.prerelease):
            if left == right:
                continue
            if left.isdigit() and right.isdigit():
                return int(left) < int(right)
            if left.isdigit() != right.isdigit():
                return left.isdigit()
            return left < right
        return len(self.prerelease) < len(other.prerelease)


_SEMVER = re.compile(
    r"^(?:v)?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)


def parse_semver(value: str) -> SemVer:
    """Parse a SemVer 2.0.0 value, accepting an optional leading ``v``."""

    match = _SEMVER.fullmatch(value.strip())
    if match is None:
        raise ValidationError(f"invalid semantic version: {value!r}")
    prerelease = tuple(match.group(4).split(".")) if match.group(4) else ()
    for identifier in prerelease:
        if identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0"):
            raise ValidationError(f"invalid semantic version: {value!r}")
    return SemVer(tuple(int(match.group(index)) for index in range(1, 4)), prerelease)


@dataclass(frozen=True)
class ReleaseSelection:
    version_text: str
    version: SemVer
    zip_name: str
    zip_url: str
    checksums_url: str
    release_notes: str = ""
    release_url: str = ""


def _release_page_url(page: int) -> str:
    if page < 1:
        raise ValidationError("GitHub release page must be positive")
    return RELEASES_URL if page == 1 else f"{RELEASES_URL}&page={page}"


def _read_release_records(timeout: int) -> list[object]:
    records: list[object] = []
    page = 1
    while True:
        batch = _read_json_url(_release_page_url(page), timeout)
        if not isinstance(batch, list):
            raise ValidationError("GitHub Releases response is not a list")
        records.extend(batch)
        if len(batch) < RELEASE_PAGE_SIZE:
            return records
        page += 1


def select_releases(timeout: int = 30) -> list[ReleaseSelection]:
    """Return usable non-draft releases published from the owner's fork."""

    candidates: list[ReleaseSelection] = []
    for record in _read_release_records(timeout):
        if not isinstance(record, dict) or record.get("draft"):
            continue
        tag_name = record.get("tag_name")
        if not isinstance(tag_name, str):
            continue
        try:
            version = parse_semver(tag_name)
        except ValidationError:
            continue
        version_text = tag_name.removeprefix("v")
        raw_assets = record.get("assets", [])
        if not isinstance(raw_assets, list):
            continue

        assets: dict[str, str] = {}
        duplicate_asset_name = False
        for asset in raw_assets:
            if (
                not isinstance(asset, dict)
                or not isinstance(asset.get("name"), str)
                or not isinstance(asset.get("browser_download_url"), str)
            ):
                continue
            name = str(asset["name"])
            if name in assets:
                duplicate_asset_name = True
                break
            assets[name] = str(asset["browser_download_url"])
        if duplicate_asset_name:
            raise ValidationError(
                f"release {tag_name} contains duplicate asset names"
            )

        zip_name = f"codex_workflow-{version_text}.zip"
        if zip_name not in assets or "SHA256SUMS" not in assets:
            continue

        zip_url = _validate_asset_url(assets[zip_name], version_text, zip_name)
        checksums_url = _validate_asset_url(
            assets["SHA256SUMS"], version_text, "SHA256SUMS"
        )
        candidates.append(
            ReleaseSelection(
                version_text,
                version,
                zip_name,
                zip_url,
                checksums_url,
                record.get("body") if isinstance(record.get("body"), str) else "",
                record.get("html_url")
                if isinstance(record.get("html_url"), str)
                else "",
            )
        )
    return sorted(candidates, key=lambda item: item.version, reverse=True)


def select_latest(timeout: int = 30) -> ReleaseSelection:
    releases = select_releases(timeout)
    if not releases:
        raise ValidationError(
            f"no {RELEASES_REPOSITORY} release has both the universal ZIP and SHA256SUMS"
        )
    return releases[0]


def summarize_release_notes(text: str, *, max_length: int = 600) -> str:
    """Render a compact plain-text summary from a GitHub release body."""

    fragments: list[str] = []
    in_code_block = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block or not line or line.startswith("<!--"):
            continue
        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+)", "", line)
        line = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        if line:
            fragments.append(line)

    summary = " ".join(fragments).strip()
    if not summary:
        return "No release notes were provided."
    if len(summary) <= max_length:
        return summary
    if max_length <= 1:
        return "…"[:max_length]
    truncated = summary[: max_length - 1].rstrip()
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0].rstrip()
    return f"{truncated}…"


def acquire(
    selection: ReleaseSelection, timeout: int = 60
) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    """Download, checksum-verify, safely extract, and return a release package."""

    _validate_asset_url(selection.zip_url, selection.version_text, selection.zip_name)
    _validate_asset_url(
        selection.checksums_url, selection.version_text, "SHA256SUMS"
    )

    temporary = tempfile.TemporaryDirectory(prefix="codex-workflow-release-")
    root = Path(temporary.name)
    try:
        archive = root / selection.zip_name
        archive.write_bytes(
            _read_url(
                selection.zip_url,
                timeout,
                max_bytes=MAX_RELEASE_DOWNLOAD_BYTES,
            )
        )
        checksum_text = _read_url(
            selection.checksums_url,
            timeout,
            max_bytes=MAX_CHECKSUM_BYTES,
        ).decode("ascii")
        expected = _checksum_for(checksum_text, selection.zip_name)
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        if actual != expected:
            raise ValidationError("release ZIP checksum mismatch")

        extraction = root / "extracted"
        extraction.mkdir()
        try:
            with zipfile.ZipFile(archive) as bundle:
                members = bundle.infolist()
                total_size = sum(member.file_size for member in members)
                if total_size > MAX_UNCOMPRESSED_BYTES:
                    raise ValidationError(
                        "release ZIP exceeds the uncompressed size limit"
                    )

                targets: set[str] = set()
                for member in members:
                    target = _validate_member(member)
                    if target in targets:
                        raise ValidationError(
                            f"release ZIP contains colliding members: {target}"
                        )
                    targets.add(target)
                bundle.extractall(extraction)
        except zipfile.BadZipFile as error:
            raise ValidationError(f"invalid release ZIP: {error}") from error

        package = extraction / "codex_workflow"
        if not package.is_dir():
            raise ValidationError("release ZIP lacks codex_workflow package root")
        return temporary, package
    except Exception:
        temporary.cleanup()
        raise


def _split_network_url(url: str) -> tuple[str, str]:
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise ValidationError(f"invalid network URL: {url}") from error
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValidationError(f"untrusted network URL: {url}")
    if parsed.username is not None or parsed.password is not None:
        raise ValidationError(f"credentials are not allowed in network URL: {url}")
    if port not in {None, 443}:
        raise ValidationError(f"non-standard HTTPS port is not allowed: {url}")
    return parsed.hostname.lower(), unquote(parsed.path)


def _validate_network_url(url: str) -> str:
    host, path = _split_network_url(url)
    repo_prefix = f"/repos/{RELEASES_REPOSITORY}/releases"
    asset_prefix = f"/{RELEASES_REPOSITORY}/releases/download/"

    if host == _GITHUB_API_HOST:
        if path != repo_prefix and not path.startswith(repo_prefix + "/"):
            raise ValidationError(f"GitHub API URL is outside the owner repository: {url}")
        return url
    if host == _GITHUB_WEB_HOST:
        if not path.startswith(asset_prefix):
            raise ValidationError(f"GitHub download URL is outside the owner repository: {url}")
        return url
    if host in _GITHUB_DOWNLOAD_HOSTS:
        return url
    raise ValidationError(f"untrusted download host: {host}")


def _validate_asset_url(url: str, version_text: str, asset_name: str) -> str:
    try:
        host, path = _split_network_url(url)
    except ValidationError as error:
        raise ValidationError(f"release asset URL is invalid: {url}") from error
    if host != _GITHUB_WEB_HOST:
        raise ValidationError(f"release asset URL must start on github.com: {url}")

    prefix = f"/{RELEASES_REPOSITORY}/releases/download/"
    if not path.startswith(prefix):
        raise ValidationError(f"release asset URL is outside the owner repository: {url}")
    remainder = path[len(prefix) :]
    tag, separator, name = remainder.partition("/")
    if (
        not separator
        or "/" in name
        or name != asset_name
        or tag not in {version_text, f"v{version_text}"}
    ):
        raise ValidationError(f"release asset URL does not match release metadata: {url}")

    parsed = urlsplit(url)
    if parsed.query or parsed.fragment:
        raise ValidationError(f"release asset URL must not contain query or fragment data: {url}")
    return url


class _TrustedRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> urllib.request.Request | None:
        _validate_network_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _read_json_url(url: str, timeout: int) -> object:
    try:
        return json.loads(_read_url(url, timeout, max_bytes=MAX_METADATA_BYTES))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValidationError(f"invalid JSON response from {url}: {error}") from error


def _read_url(url: str, timeout: int, *, max_bytes: int = MAX_METADATA_BYTES) -> bytes:
    if max_bytes < 1:
        raise ValidationError("network download size limit must be positive")
    _validate_network_url(url)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "elmakus-codex-workflow-runtime"},
    )
    opener = urllib.request.build_opener(_TrustedRedirectHandler())
    try:
        with opener.open(request, timeout=timeout) as response:
            final_url = response.geturl()
            _validate_network_url(final_url)
            content_length = response.headers.get("Content-Length")
            if content_length is not None:
                try:
                    declared = int(content_length)
                except ValueError as error:
                    raise ValidationError(
                        f"invalid Content-Length from {final_url}"
                    ) from error
                if declared > max_bytes:
                    raise ValidationError(
                        f"network response exceeds {max_bytes} byte limit"
                    )
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise ValidationError(
                    f"network response exceeds {max_bytes} byte limit"
                )
            return data
    except ValidationError:
        raise
    except (OSError, urllib.error.URLError) as error:
        raise ValidationError(f"network request failed for {url}: {error}") from error


def _checksum_for(text: str, filename: str) -> str:
    matches: list[str] = []
    pattern = re.compile(r"^([0-9A-Fa-f]{64}) ([ *])(.+)$")
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line:
            continue
        match = pattern.fullmatch(line)
        if match is None:
            raise ValidationError(
                f"SHA256SUMS contains a malformed entry on line {line_number}"
            )
        digest, marker, listed_name = match.groups()
        if marker == "*" and listed_name.startswith("*"):
            raise ValidationError(
                f"SHA256SUMS contains an invalid binary marker on line {line_number}"
            )
        if listed_name == filename:
            matches.append(digest.lower())
    if len(matches) != 1:
        raise ValidationError(f"SHA256SUMS lacks one unique valid entry for {filename}")
    return matches[0]


def _validate_member(member: zipfile.ZipInfo) -> str:
    name = member.filename
    if not name or "\x00" in name or "\\" in name:
        raise ValidationError(f"unsafe ZIP member: {name!r}")

    normalized = name.rstrip("/")
    path = PurePosixPath(normalized)
    if path.is_absolute() or ".." in path.parts:
        raise ValidationError(f"unsafe ZIP member: {name}")
    canonical = path.as_posix()
    if not canonical or normalized != canonical:
        raise ValidationError(f"non-canonical ZIP member: {name}")
    if not (
        canonical == "codex_workflow"
        or canonical.startswith("codex_workflow/")
    ):
        raise ValidationError(f"ZIP member outside package root: {name}")

    file_type = (member.external_attr >> 16) & 0o170000
    if file_type == 0o120000:
        raise ValidationError(f"release ZIP contains a symlink: {name}")
    if file_type not in {0, 0o040000, 0o100000}:
        raise ValidationError(f"release ZIP contains a special filesystem entry: {name}")
    return canonical
