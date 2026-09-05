"""Semantic-version helpers for explicit local workflow migrations.

The private runtime deliberately has no release-discovery or download path.
Callers must supply a reviewed local package to the lifecycle command.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering

from .errors import ValidationError


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
