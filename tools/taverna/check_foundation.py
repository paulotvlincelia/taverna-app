"""Check the Taverna-owned contribution surface, never claim an iOS build."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote

BASE = "479548ee53ffb73db73841e77acbeee5a78dbbd5"


def check(root: Path, release_assets: bool = False) -> list[str]:
    errors: list[str] = []
    required = ["README.md", "README.upstream.md", "AGENTS.md", "CLAUDE.md",
                "CONTRIBUTING.md", "LICENSE", "assets/ASSETS_LICENSE.md",
                "docs/taverna/asset-policy.json", "docs/taverna/upstream.json",
                ".github/workflows/foundation.yml"]
    for path in required:
        if not (root / path).is_file():
            errors.append(f"missing: {path}")
    try:
        origin = json.loads((root / "docs/taverna/upstream.json").read_text())
        if origin["repository"] != "simplex-chat/simplex-chat" or origin["sha"] != BASE:
            errors.append("upstream: repository/SHA mismatch")
        for path, digest in origin["preserved"].items():
            if hashlib.sha256((root / path).read_bytes()).hexdigest() != digest:
                errors.append(f"preserved license changed: {path}")
        if set(origin["preserved"]) != {"LICENSE", "assets/ASSETS_LICENSE.md"}:
            errors.append("upstream: both licenses must be preserved")
        policy = json.loads((root / "docs/taverna/asset-policy.json").read_text())
        if policy != {"schema": 1, "release_status": "BLOCKED",
                      "reason": "Inventário individual e assets próprios/permissões pendentes.",
                      "approved_assets": [], "upstream_sha": BASE}:
            errors.append("assets: foundation must remain BLOCKED with no approved assets")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"metadata invalid: {exc}")
    if release_assets:
        errors.append("BLOCKED: asset inventory/permissions and corresponding-source release proof required")
    claude = root / "CLAUDE.md"
    if claude.is_file() and ("[AGENTS.md](AGENTS.md)" not in claude.read_text()
                             or len(claude.read_text().splitlines()) > 6):
        errors.append("CLAUDE.md must redirect to AGENTS.md")
    docs = [root / n for n in ("README.md", "AGENTS.md", "CLAUDE.md", "CONTRIBUTING.md")]
    for directory in ("docs/taverna", ".specs/features/foundation", ".agents/skills"):
        docs.extend((root / directory).rglob("*.md"))
    for path in docs:
        if not path.is_file():
            continue
        text = path.read_text()
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip("<>").split("#", 1)[0]
            if not target or re.match(r"[a-zA-Z]+:", target):
                continue
            if not (path.parent / unquote(target)).exists():
                errors.append(f"{path.relative_to(root)}: broken link {target}")
        # Taverna-owned prose cannot carry local inventory or real access material.
        if re.search(r"/Users/[^/\s]+/|100\.(?:[6-9]\d|1[01]\d|12[0-7])\.\d+\.\d+|-----BEGIN .*PRIVATE KEY", text):
            errors.append(f"{path.relative_to(root)}: private access material")
    workflows = sorted(p.name for p in (root / ".github/workflows").glob("*.*"))
    if workflows != ["foundation.yml"]:
        errors.append("only Foundation workflow may be active")
    workflow = root / ".github/workflows/foundation.yml"
    if workflow.is_file():
        text = workflow.read_text()
        if "contents: read" not in text or any(word in text for word in
                ("secrets.", "pull_request_target", "contents: write", "id-token: write")):
            errors.append("workflow must be unprivileged and secret-free")
    for skill in ("tlc-spec-lean", "tlc-spec-driven"):
        directory = root / ".agents/skills" / skill
        for name in ("SKILL.md", "NOTICE.md"):
            if not (directory / name).is_file():
                errors.append(f"skill attribution missing: {skill}/{name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--release-assets", action="store_true")
    args = parser.parse_args()
    errors = check(args.root, args.release_assets)
    print("\n".join(errors) if errors else "PASS: foundation only; no iOS build or release proof")
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
