#!/usr/bin/env python3
"""One-time archival notice and original-source preservation check; no runtime imports."""

import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[2]
policy = json.loads((root / "RETIRED.json").read_text())
EXPECTED_REPOSITORY = "ivanivanka/meetup-gmail-calendar-sync"
EXPECTED_BASE = "a4211160c4b5b9d170da2128961ee3200eaafeb9"
EXPECTED_NOTICES = [
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "RETIRED.md",
]
assert policy["repository"] == EXPECTED_REPOSITORY
assert policy["original_head"] == EXPECTED_BASE
assert policy["notice_surfaces"] == EXPECTED_NOTICES
assert policy["status"] == "permanently_retired"
assert policy["historical_read"]["explicit_confirmations_required"] == 2
assert policy["historical_read"]["current_task_only"] is True
assert policy["historical_read"]["ordinary_reads_allowed"] is False
assert policy["active_client_content_must_not_be_overwritten"] is True
assert policy["external_resource_teardown"] == "requires_separate_current_provider_evidence"
required = {
    "write",
    "commit",
    "push",
    "pull",
    "fetch",
    "clone",
    "sync",
    "install",
    "build",
    "run",
    "deploy",
    "schedule",
    "revive",
    "maintain",
    "service_use",
}
assert required <= set(policy["prohibited_operations"])
base = EXPECTED_BASE
subprocess.run(["git", "cat-file", "-e", base + "^{commit}"], cwd=root, check=True)
entries = subprocess.check_output(["git", "ls-tree", "-rz", base], cwd=root).split(b"\0")
notices = set(EXPECTED_NOTICES)
preserved = 0
original_names = set()
for entry in entries:
    if not entry:
        continue
    metadata, path_bytes = entry.split(b"\t", 1)
    mode, kind, oid = metadata.split(b" ")
    name = path_bytes.decode("utf-8", "surrogateescape")
    original_names.add(name)
    old = subprocess.check_output(["git", "cat-file", "blob", oid.decode()], cwd=root)
    path = root / name
    assert path.is_file(), "Original file missing: " + name
    new = path.read_bytes()
    if name in notices:
        assert new.endswith(old), "Original notice-file bytes changed: " + name
    else:
        assert new == old, "Historical content changed: " + name
    tracked = subprocess.check_output(["git", "ls-files", "--stage", "--", name], cwd=root).split(
        b" ", 1
    )[0]
    assert tracked == mode, "Original file mode changed: " + name
    preserved += 1
tracked_names = set(
    subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    .decode("utf-8", "surrogateescape")
    .split("\0")
) - {""}
allowed_additions = notices | {
    "RETIRED.json",
    ".github/scripts/validate-retirement.py",
    ".github/workflows/retirement-preservation.yml",
}
assert tracked_names - original_names <= allowed_additions, "Unrelated files added"
for name in notices:
    value = (root / name).read_text()
    assert "ARCHIVAL SOURCE ONLY - RETIRED" in value, name
    assert "two separate explicit confirmations" in value, name
    assert "current task" in value, name
    assert (
        "Do not write, commit, push, pull, fetch, clone, sync, install, "
        "build, run, deploy, schedule, revive or maintain" in value
    ), name
print(
    f"PASS: {preserved} original files preserved; retirement policy "
    f"and {len(notices)} warning surfaces verified."
)
