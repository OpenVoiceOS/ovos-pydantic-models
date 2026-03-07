#!/usr/bin/env python3
"""Scan the OVOS workspace for bus message types and compare against modeled messages.

Usage:
    python tools/scan_for_messages.py [--workspace PATH] [--output PATH] [--unmodeled-only]

Outputs a Markdown report of:
  - All message types found in the workspace (by source file)
  - Which are already modeled in ovos_pydantic_models
  - Which are not yet modeled (candidates for new models)

The script is intentionally conservative — it only reports messages it is
confident about, and groups them by likely subsystem.
"""
from __future__ import annotations

import argparse
import ast
import importlib
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WORKSPACE_DEFAULT = Path(__file__).parent.parent.parent  # …/OpenVoiceOS Workspace

# Repos to skip entirely (no OVOS bus messages, or private external deps)
SKIP_REPOS = {
    "gh-automations",
    "ovos-benchmarks-docker",
    "ovos-docker",
    "ovos-docker-simple",
    "ovos-docker-stt",
    "ovos-docker-tts",
    "ovos-docker-tx",
    "ovos-landing-page",
    "ovos-blogs",
    "ovos-ww-community-dataset",
    "ovos-docs-viewer",
    "ovos-foundation",
    "raspOVOS",
    "ovos-hub",
    "ovos-busmon",
    "ovoscope",
    "ovos-diagnostics",
    "=2.0",
}

# Directories inside repos to ignore (venvs, caches, etc.)
SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", ".tox", "node_modules",
             "build", "dist", ".eggs"}

# ---------------------------------------------------------------------------
# Patterns that extract a literal message type string from Python source
# ---------------------------------------------------------------------------

# Matches: add_event("msg.type", ...) or bus.on("msg.type", ...)
# or bus.emit(Message("msg.type", ...))
# Groups the quoted string immediately after the call/constructor.
_PATTERNS = [
    # self.add_event("foo.bar", ...) / self.add_event('foo.bar', ...)
    re.compile(r'\.add_event\s*\(\s*["\']([^"\']+)["\']'),
    # bus.on("foo.bar") / self.bus.on("foo.bar")
    re.compile(r'\.bus\.on\s*\(\s*["\']([^"\']+)["\']'),
    re.compile(r'\bbus\.on\s*\(\s*["\']([^"\']+)["\']'),
    # bus.emit(Message("foo.bar"))
    re.compile(r'\.bus\.emit\s*\(\s*Message\s*\(\s*["\']([^"\']+)["\']'),
    re.compile(r'\bbus\.emit\s*\(\s*Message\s*\(\s*["\']([^"\']+)["\']'),
    # bus.wait_for_response(Message("foo.bar"))
    re.compile(r'\.bus\.wait_for_response\s*\(\s*Message\s*\(\s*["\']([^"\']+)["\']'),
    # message.forward("foo.bar")
    re.compile(r'\.forward\s*\(\s*["\']([^"\']+)["\']'),
    # message.response(... "foo.bar" ...) – less common, skip to avoid FP
]

# Heuristic filters — skip anything that looks like a variable or dialog key
_NOISE_RE = re.compile(
    r'^(message|msg|event|type|name|{|.*\{.*\}|.*%.*|.*\.dialog$|.*\.voc$|'
    r'speak|start|stop|pause|resume|next|prev|play|yes|no|true|false|ok|done|'
    r'error|success|fail|None|self\.|bus\.|data\.|response$|request$)$',
    re.IGNORECASE,
)


def looks_like_message_type(s: str) -> bool:
    """Return True if the string looks like a bus message type."""
    if not s or len(s) < 3 or len(s) > 120:
        return False
    if _NOISE_RE.match(s):
        return False
    # must contain at least one dot or colon (namespace separator)
    if "." not in s and ":" not in s:
        return False
    # skip obvious non-message strings
    if s.startswith(("http", "file:", "/", "\\", "~", ".", " ")):
        return False
    if "\n" in s or "\t" in s:
        return False
    return True


# ---------------------------------------------------------------------------
# Collect modeled message types from ovos_pydantic_models
# ---------------------------------------------------------------------------

def collect_modeled(models_root: Path) -> dict[str, str]:
    """Return {message_type: module_path} for every OpenVoiceOSMessage subclass."""
    modeled: dict[str, str] = {}
    pkg_root = models_root / "ovos_pydantic_models"
    if not pkg_root.exists():
        return modeled

    for py in sorted(pkg_root.rglob("*.py")):
        rel = py.relative_to(models_root)
        try:
            src = py.read_text(errors="replace")
        except Exception:
            continue
        # Find message_type = "..." assignments — simple but fast
        for m in re.finditer(r'message_type\s*:\s*str\s*=\s*["\']([^"\']+)["\']', src):
            mt = m.group(1)
            if mt not in modeled:
                modeled[mt] = str(rel)
    return modeled


# ---------------------------------------------------------------------------
# Scan workspace repos for message types
# ---------------------------------------------------------------------------

def scan_repo(repo_path: Path) -> dict[str, list[str]]:
    """Scan a single repo. Returns {message_type: [file:line, ...]}."""
    found: dict[str, list[str]] = defaultdict(list)
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = Path(root) / fname
            rel = fpath.relative_to(repo_path)
            try:
                lines = fpath.read_text(errors="replace").splitlines()
            except Exception:
                continue
            for i, line in enumerate(lines, 1):
                for pat in _PATTERNS:
                    for m in pat.finditer(line):
                        mt = m.group(1)
                        if looks_like_message_type(mt):
                            ref = f"{rel}:{i}"
                            if ref not in found[mt]:
                                found[mt].append(ref)
    return found


# ---------------------------------------------------------------------------
# Subsystem grouping heuristics
# ---------------------------------------------------------------------------

def guess_subsystem(mt: str, repo: str) -> str:
    """Guess the subsystem for a message type."""
    p = mt.lower()
    if p.startswith("system."):
        return "phal.system"
    if p.startswith("ovos.phal.nm.") or p.startswith("ovos.phal.wifi"):
        return "phal.network_manager"
    if p.startswith("ovos.phal.camera"):
        return "phal.camera"
    if p.startswith("ovos.phal.sensor") or p.startswith("ovos.phal.binary"):
        return "phal.sensors"
    if p.startswith("ovos.wallpaper") or p.startswith("homescreen.wallpaper"):
        return "phal.wallpaper"
    if p.startswith("ovos.phal."):
        return "phal.other"
    if p.startswith("oauth."):
        return "phal.oauth"
    if p.startswith("ovos.common_play.") or p.startswith("ocp."):
        return "skills.ocp"
    if p.startswith("ovos.common_query.") or p.startswith("common_query.") or p.startswith("question:"):
        return "skills.common_query"
    if p.startswith("ovos.skills.fallback."):
        return "intents.fallbacks"
    if p.startswith("skill.converse.") or p.startswith("ovos.skills.converse"):
        return "intents.converse"
    if p.startswith("mycroft.skills."):
        return "core.skill_manager"
    if p.startswith("ovos.skills."):
        return "core.skill_manager"
    if p.startswith("ovos.session."):
        return "core.session"
    if p.startswith("mycroft.scheduler."):
        return "core.scheduler"
    if p.startswith("configuration."):
        return "core.configuration"
    if p.startswith("recognizer_loop.") or p.startswith("ovos.microphone.") or p.startswith("opm."):
        return "listener"
    if p.startswith("mycroft.audio.") or p.startswith("ovos.audio.") or p.startswith("speak"):
        return "audio"
    if p.startswith("mycroft.volume.") or p.startswith("ovos.volume."):
        return "phal.alsa"
    if p.startswith("enclosure."):
        return "phal.enclosure"
    if p.startswith("gui.") or p.startswith("mycroft.gui.") or p.startswith("homescreen.") or p.startswith("ovos.homescreen."):
        return "gui"
    if p.startswith("ovos.notification.") or p.startswith("ovos.widgets."):
        return "gui.notifications"
    if p.startswith("intent.service.") or p.startswith("ovos.utterance."):
        return "intents.core"
    if p.startswith("add_context") or p.startswith("remove_context") or p.startswith("clear_context"):
        return "intents.core"
    if p.startswith("register_") or p.startswith("detach_"):
        return "intents.adapt"
    if p.startswith("padatious:"):
        return "intents.padatious"
    if p.startswith("persona:"):
        return "skills.persona"
    if p.startswith("hive.") or p.startswith("hass.") or p.startswith("ovos.mass."):
        return "external"
    if p.startswith("ovos.pip.") or p.startswith("ovos.skills.install"):
        return "core.installer"
    if p.startswith("ggwave."):
        return "skills.ggwave"
    if p.startswith("ovos.shell."):
        return "gui.shell"
    if "repo" in locals() and "PHAL" in repo:
        return "phal.other"
    return "other"


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    workspace: Path,
    models_root: Path,
    unmodeled_only: bool = False,
) -> str:
    modeled = collect_modeled(models_root)
    modeled_set = set(modeled.keys())

    repos = sorted(
        [d for d in workspace.iterdir()
         if d.is_dir() and d.name not in SKIP_REPOS and not d.name.startswith(".")],
        key=lambda p: p.name,
    )

    # {message_type: {repo_name: [refs]}}
    all_found: dict[str, dict[str, list[str]]] = defaultdict(dict)

    for repo in repos:
        if repo.name == "ovos-pydantic-models":
            continue  # skip self
        hits = scan_repo(repo)
        for mt, refs in hits.items():
            all_found[mt][repo.name] = refs

    # Separate modeled vs unmodeled
    unmodeled: dict[str, dict[str, list[str]]] = {}
    already: dict[str, str] = {}
    for mt, sources in sorted(all_found.items()):
        if mt in modeled_set:
            already[mt] = modeled[mt]
        else:
            unmodeled[mt] = sources

    # Group unmodeled by subsystem
    by_subsystem: dict[str, list[tuple[str, dict[str, list[str]]]]] = defaultdict(list)
    for mt, sources in sorted(unmodeled.items()):
        repo_name = next(iter(sources))
        sub = guess_subsystem(mt, repo_name)
        by_subsystem[sub].append((mt, sources))

    lines: list[str] = []
    lines.append("# OVOS Bus Message Scan Report\n")
    lines.append(f"Workspace: `{workspace}`\n")
    lines.append(f"Models root: `{models_root}`\n")
    lines.append(f"**Modeled:** {len(modeled_set)} | "
                 f"**Found in workspace:** {len(all_found)} | "
                 f"**Unmodeled:** {len(unmodeled)}\n")

    if not unmodeled_only:
        lines.append("\n---\n")
        lines.append("## Already Modeled (found in workspace + in ovos_pydantic_models)\n")
        lines.append(f"{len(already)} message types confirmed used and modeled.\n")
        lines.append("<details><summary>Show list</summary>\n")
        lines.append("")
        for mt in sorted(already):
            lines.append(f"- `{mt}` → `{already[mt]}`")
        lines.append("")
        lines.append("</details>\n")

    lines.append("\n---\n")
    lines.append("## Unmodeled Messages (candidates for new models)\n")
    lines.append(f"Total: **{len(unmodeled)}** unmodeled message types found.\n")

    for subsystem in sorted(by_subsystem):
        msgs = by_subsystem[subsystem]
        lines.append(f"\n### `{subsystem}` ({len(msgs)} messages)\n")
        lines.append("| Message type | Sources |")
        lines.append("|---|---|")
        for mt, sources in msgs:
            # Compact: just list repos
            src_str = ", ".join(
                f"`{repo}`" for repo in sorted(sources)[:3]
            )
            if len(sources) > 3:
                src_str += f" (+{len(sources)-3} more)"
            lines.append(f"| `{mt}` | {src_str} |")

    lines.append("\n---\n")
    lines.append("## All Modeled Types (not found in workspace scan)\n")
    modeled_only = {mt: path for mt, path in modeled.items()
                   if mt not in all_found}
    lines.append(f"{len(modeled_only)} modeled types not encountered in this scan "
                 "(may be emitted by services not in the workspace, "
                 "or found via string-building).\n")
    if modeled_only:
        lines.append("<details><summary>Show list</summary>\n")
        lines.append("")
        for mt in sorted(modeled_only):
            lines.append(f"- `{mt}` (`{modeled_only[mt]}`)")
        lines.append("")
        lines.append("</details>\n")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def inspect_message(workspace: Path, message_type: str, context_lines: int = 6) -> str:
    """Show source context for every occurrence of a message type in the workspace."""
    lines: list[str] = []
    lines.append(f"# Occurrences of `{message_type}`\n")
    found_any = False
    for repo in sorted(workspace.iterdir()):
        if not repo.is_dir() or repo.name in SKIP_REPOS or repo.name.startswith("."):
            continue
        for root, dirs, files in os.walk(repo):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for fname in files:
                if not fname.endswith(".py"):
                    continue
                fpath = Path(root) / fname
                rel = fpath.relative_to(workspace)
                try:
                    src_lines = fpath.read_text(errors="replace").splitlines()
                except Exception:
                    continue
                for i, line in enumerate(src_lines):
                    if message_type in line:
                        start = max(0, i - 2)
                        end = min(len(src_lines), i + context_lines)
                        lines.append(f"## `{rel}:{i+1}`\n")
                        lines.append("```python")
                        for j in range(start, end):
                            prefix = ">>>" if j == i else "   "
                            lines.append(f"{prefix} {j+1:4d}  {src_lines[j]}")
                        lines.append("```\n")
                        found_any = True
    if not found_any:
        lines.append(f"No occurrences found for `{message_type}` in workspace.\n")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", default=str(WORKSPACE_DEFAULT),
                    help="Path to the OpenVoiceOS workspace root")
    ap.add_argument("--output", default=None,
                    help="Write report to this file (default: stdout)")
    ap.add_argument("--unmodeled-only", action="store_true",
                    help="Only output the unmodeled messages section")
    ap.add_argument("--inspect", default=None, metavar="MSG_TYPE",
                    help="Show source context for every occurrence of this message type")
    ap.add_argument("--context", type=int, default=6,
                    help="Number of context lines to show in --inspect mode (default: 6)")
    args = ap.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    models_root = workspace / "ovos-pydantic-models"

    print(f"Scanning workspace: {workspace}", file=sys.stderr)
    print(f"Models root:        {models_root}", file=sys.stderr)

    if args.inspect:
        report = inspect_message(workspace, args.inspect, args.context)
    else:
        report = generate_report(workspace, models_root, args.unmodeled_only)

    if args.output:
        Path(args.output).write_text(report)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
