# M03-T02 corrective implementation evidence

Status: implementation complete; fresh independent re-review required
Corrected review subject: `3e6f86cb78b54c8690b386d8575fc2647465eed3`
Prior RED subject: `b07e93a29aa70f97e585bbdaf5b41e8a44d1ea5e`
Prior RED evidence: `implementation/workstreams/upstream-1-1-18-alignment/evidence/M03-T02-review-recovery.md`
Pull request: #7

## Correction

The recovered RED finding showed that the installed operator command dispatcher still advertised two retired profile forms. The correction is intentionally bounded to the existing M03-T02 authority:

- removed `codex_workflow --profile luna-xhigh` from `codex_workflow/operate/user_AGENTS.md`;
- removed `codex_workflow --profile pro-x5` from the same active command-dispatch surface;
- added focused runtime regression assertions requiring `plus` and `muse-max` command forms and rejecting both retired forms.

No compute-profile runtime mapping, Muse lifecycle, worker topology, Material Event Push behavior, platform-settings ownership, VERSION, release, or publication behavior changed.

## Verification

Exact corrected subject `3e6f86cb78b54c8690b386d8575fc2647465eed3`:

- GitHub Actions Tests run #155 (`35498131939`): GREEN on the exact commit.
- Runtime regression suite: 97/97 GREEN.
- Muse adapter regression suite: 33/33 GREEN.
- Muse Max profile regression suite: 7/7 GREEN.
- Python compile check: GREEN.
- Package validation: GREEN.
- Package build and archive verification: GREEN.
- Exact-subject static readback: only `codex_workflow --profile plus` and `codex_workflow --profile muse-max` remain as explicit profile-switch command forms in the installed dispatcher; retired command forms are absent.
- Active orchestration/profile contract scan remains free of `luna-xhigh` / `pro-x5` supported-path references and Muse unavailable-push/emulation pseudo-contract text.
- `codex_workflow/operate/VERSION`: unchanged at `1.1.17-private.12`.

## Review boundary

M03-T02 remains non-terminal. Because this chat implemented the corrected subject, REQUIRED independent review must be performed by a fresh chat before Card or milestone completion.
