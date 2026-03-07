#!/usr/bin/env python3
"""Generate a static documentation website for the OVOS MessageBus protocol.

Usage:
    python tools/generate_site.py [output_dir]

    Default output: site/index.html

For GitHub Pages: commit the site/ directory and configure Pages to serve
from the /site folder (Settings → Pages → Source → /site).
"""

import importlib
import inspect
import json
import pkgutil
import re
import sys
from pathlib import Path
from typing import Any, Union, get_args, get_origin

sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import BaseModel

import ovos_pydantic_models
from ovos_pydantic_models.message import OpenVoiceOSMessage

# ---------------------------------------------------------------------------
# Subsystem mapping: module_suffix → (category, label)
# ---------------------------------------------------------------------------
SUBSYSTEM_MAP = {
    "audio.playback":           ("Audio",    "Playback / TTS"),
    "audio.audioservice":       ("Audio",    "Audio Service"),
    "audio.opm":                ("Audio",    "OPM Queries"),
    "audio.recognizer_loop":    ("Audio",    "Recognizer Loop"),
    "audio.ocp":                ("OCP",      "Core Protocol"),
    "audio.video_service":      ("OCP",      "Video Service"),
    "audio.web_service":        ("OCP",      "Web Service"),
    "skills.ocp":               ("OCP",      "Skill API"),
    "listener.recognizer_loop": ("Listener", "Recognizer Loop"),
    "listener.opm":             ("Listener", "OPM Queries"),
    "intents.core":             ("Intents",  "Core / Context"),
    "intents.converse":         ("Intents",  "Converse"),
    "intents.fallbacks":        ("Intents",  "Fallback"),
    "intents.stop":             ("Intents",  "Stop"),
    "intents.adapt":            ("Intents",  "Adapt"),
    "intents.padatious":        ("Intents",  "Padatious"),
    "skills.common_query":      ("Skills",   "Common Query"),
    "skills.game":              ("Skills",   "Game"),
    "skills.converse":          ("Skills",   "Converse"),
    "skills.fallback":          ("Skills",   "Fallback"),
    "core.skill_manager":       ("Core",     "Skill Manager"),
    "core.skill_installer":     ("Core",     "Installer"),
    "core.skill_settings":      ("Core",     "Settings"),
    "core.session":             ("Core",     "Session"),
    "core.configuration":       ("Core",     "Configuration"),
    "core.scheduler":           ("Core",     "Scheduler"),
    "gui.homescreen":           ("GUI",      "Homescreen"),
    "gui.namespace":            ("GUI",      "Namespace / Pages"),
    "gui.media_player":         ("GUI",      "Media Player"),
    "gui.notifications":        ("GUI",      "Notifications"),
    "gui.widgets":              ("GUI",      "Widgets"),
    "phal.connectivity":        ("PHAL",     "Connectivity"),
    "phal.volume":              ("PHAL",     "Volume"),
    "phal.system":              ("PHAL",     "System"),
    "phal.network_manager":     ("PHAL",     "Network Manager"),
    "phal.wifi_setup":          ("PHAL",     "WiFi Setup"),
    "phal.brightness":          ("PHAL",     "Brightness"),
    "phal.wallpaper":           ("PHAL",     "Wallpaper"),
    "phal.camera":              ("PHAL",     "Camera"),
    "phal.sensors":             ("PHAL",     "Sensors"),
    "phal.configuration_provider": ("PHAL", "Config Provider"),
    "phal.oauth":               ("PHAL",     "OAuth"),
    "phal.enclosure":           ("PHAL",     "Enclosure (Mark1)"),
}

# Subsystems that are fully deprecated. Classes in these modules will be
# tagged with deprecated=True in the JSON data and flagged in the UI.
# Only list subsystems whose backing plugin/package is archived on GitHub
# per PACKAGE_INVENTORY.md. Do not guess — verify before adding.
DEPRECATED_SUBSYSTEMS = {
    "phal.configuration_provider",  # ovos-PHAL-plugin-configuration-provider archived
    "phal.wifi_setup",              # ovos-PHAL-plugin-wifi-setup archived
    "gui.media_player",             # superseded by OCP / ovos-media GUI player
    "gui.widgets",                  # superseded by new homescreen/GUI rewrite
    "gui.homescreen",               # superseded by new homescreen/GUI rewrite
    "gui.notifications",            # superseded by new GUI rewrite
}

# Subsystems that still work but have better or upcoming alternatives.
# Not deprecated — just not the recommended path for new code.
LEGACY_SUBSYSTEMS = {
    # mycroft.audio service; being superseded by OCP (ovos-media) for media
    # and by the direct audio pipeline for TTS
    "audio.audioservice",
    # Adapt (keyword-based) and Padatious (ML) intent engines are superseded by
    # Padacioso / ML-based pipelines.
    "intents.adapt",
    "intents.padatious",
}

# Subsystems that exist and are being actively developed but have NOT had an
# official stable release yet. Messages may change without notice.
# Only list subsystems whose backing project is confirmed pre-release/WIP
# per PACKAGE_INVENTORY.md.
BETA_SUBSYSTEMS = {
    # ovos-gui is undergoing a full rewrite; GUI message protocol is unstable
    "gui.namespace",
    # ovos-media is still 0.0.1a*, not officially launched
    "audio.video_service",
    "audio.web_service",
}

CATEGORY_ORDER = ["Audio", "OCP", "Listener", "Intents", "Skills", "Core", "GUI", "PHAL", "Other"]


# ---------------------------------------------------------------------------
# Type annotation helpers
# ---------------------------------------------------------------------------

def format_type(annotation) -> str:
    """Convert a Python type annotation to a readable string."""
    if annotation is None or annotation is type(None):
        return "null"

    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1 and len(args) == 2:
            return format_type(non_none[0]) + "?"
        return " | ".join(format_type(a) for a in non_none)

    if origin is list:
        inner = format_type(args[0]) if args else "Any"
        return f"list[{inner}]"

    if origin is dict:
        if args and len(args) >= 2:
            return f"dict[{format_type(args[0])}, {format_type(args[1])}]"
        return "dict"

    if origin is tuple:
        if args:
            return f"tuple[{', '.join(format_type(a) for a in args)}]"
        return "tuple"

    if inspect.isclass(annotation):
        return annotation.__name__

    s = str(annotation)
    for prefix in ("typing.", "typing_extensions."):
        s = s.replace(prefix, "")
    return s


def get_data_model(field_info) -> type | None:
    """Return the BaseModel subclass for a data field, or None."""
    ann = field_info.annotation
    if ann is None:
        return None

    origin = get_origin(ann)
    if origin is Union:
        args = [a for a in get_args(ann) if a is not type(None)]
        if len(args) == 1:
            ann = args[0]
        else:
            return None

    if (inspect.isclass(ann)
            and issubclass(ann, BaseModel)
            and ann is not BaseModel
            and ann.__name__ not in ("MessageData",)):
        return ann

    return None


def extract_fields(model_cls: type) -> list[dict]:
    """Extract field metadata from a BaseModel subclass."""
    fields = []
    for name, fi in model_cls.model_fields.items():
        required = fi.is_required()

        default = None
        if not required:
            if fi.default is not None and not callable(fi.default):
                try:
                    default = repr(fi.default)
                except Exception:
                    default = "…"
            elif fi.default_factory is not None:
                try:
                    val = fi.default_factory()
                    default = repr(val)
                except Exception:
                    default = "…"

        fields.append({
            "name": name,
            "type": format_type(fi.annotation),
            "required": required,
            "default": default,
            "description": fi.description or "",
        })

    # Indicate extra='allow' on the model
    cfg = getattr(model_cls, "model_config", {})
    extra = cfg.get("extra", "ignore") if isinstance(cfg, dict) else getattr(cfg, "extra", "ignore")
    if str(extra) in ("allow", "extra.allow"):
        fields.append({
            "name": "…",
            "type": "Any",
            "required": False,
            "default": None,
            "description": "(allows additional fields)",
        })

    return fields


# ---------------------------------------------------------------------------
# Introspect all message classes
# ---------------------------------------------------------------------------

def collect_messages() -> list[dict]:
    messages = []
    seen = set()

    # Walk all .py files directly so we don't miss directories without __init__.py
    pkg_root = Path(ovos_pydantic_models.__file__).parent
    module_names = []
    for py in sorted(pkg_root.rglob("*.py")):
        rel = py.relative_to(pkg_root.parent)
        mod_name = str(rel).replace("/", ".").replace("\\", ".").removesuffix(".py")
        # skip __init__ re-export files at top-level and sub-package roots
        if mod_name.endswith("__init__"):
            continue
        module_names.append(mod_name)

    for mod_name in module_names:
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"  skip {mod_name}: {e}", file=sys.stderr)
            continue

        module_suffix = mod_name.replace("ovos_pydantic_models.", "")
        category, subsystem = SUBSYSTEM_MAP.get(module_suffix, ("Other", module_suffix))
        deprecated = module_suffix in DEPRECATED_SUBSYSTEMS
        beta = module_suffix in BETA_SUBSYSTEMS
        legacy = module_suffix in LEGACY_SUBSYSTEMS

        for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
            if (not issubclass(cls, OpenVoiceOSMessage)
                    or cls is OpenVoiceOSMessage
                    or cls.__module__ != mod_name
                    or cls_name in seen):
                continue
            seen.add(cls_name)

            # message_type value
            mt_field = cls.model_fields.get("message_type")
            default_val = getattr(mt_field, "default", None) if mt_field else None
            # Avoid PydanticUndefined / sentinel objects
            is_dynamic = False
            if (default_val is not None
                    and isinstance(default_val, str)
                    and default_val not in ("", "...")):
                message_type = default_val
            else:
                # Try to extract format pattern from field description
                # e.g. "Dynamic: '{skill_id}.converse.request'." → "{skill_id}.converse.request"
                desc = (mt_field.description or "") if mt_field else ""
                m = re.search(r"'([^']+)'", desc)
                message_type = m.group(1) if m else "(dynamic)"
                is_dynamic = True

            # data fields
            data_field = cls.model_fields.get("data")
            data_model = get_data_model(data_field) if data_field else None
            data_fields = extract_fields(data_model) if data_model else []
            has_typed_data = data_model is not None

            docstring = (cls.__doc__ or "").strip()
            # Remove leading class name from docstring if pydantic added it
            if docstring.startswith(cls_name):
                docstring = ""

            # Check if the docstring itself contains a deprecation marker.
            # "superseded by" goes to legacy only — not deprecated.
            doc_legacy = legacy or any(
                kw in docstring.lower()
                for kw in ("**legacy**", "superseded by", "prefer using", "use instead")
            )
            doc_deprecated = deprecated or (not doc_legacy and any(
                kw in docstring.lower()
                for kw in ("**deprecated**", "discontinued", "is archived")
            ))
            doc_beta = beta or any(
                kw in docstring.lower()
                for kw in ("**beta**", "pre-release", "work in progress", "not yet released")
            )

            messages.append({
                "id": cls_name,
                "message_type": message_type,
                "is_dynamic": is_dynamic,
                "class_name": cls_name,
                "module": module_suffix,
                "category": category,
                "subsystem": subsystem,
                "docstring": docstring,
                "data_fields": data_fields,
                "has_typed_data": has_typed_data,
                "deprecated": doc_deprecated,
                "beta": doc_beta,
                "legacy": doc_legacy,
            })

    # Sort: category order, then subsystem, then message_type
    cat_idx = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    messages.sort(key=lambda m: (
        cat_idx.get(m["category"], 99),
        m["subsystem"],
        m["message_type"],
    ))
    return messages


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OVOS MessageBus Protocol Reference</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
/* ---- Reset & Base ---- */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 15px; scroll-behavior: smooth; }
body {
  font-family: 'Inter', system-ui, sans-serif;
  background: #0d1117;
  color: #c9d1d9;
  min-height: 100vh;
  line-height: 1.5;
}

/* ---- Variables ---- */
:root {
  --header-h: 56px;
  --sidebar-w: 240px;
  --surface: #161b22;
  --surface2: #21262d;
  --border: #30363d;
  --text: #c9d1d9;
  --text-muted: #8b949e;
  --text-dim: #484f58;
  --accent: #58a6ff;
  --radius: 8px;
  --cat-audio:    #a78bfa;
  --cat-ocp:      #f43f5e;
  --cat-listener: #60a5fa;
  --cat-intents:  #34d399;
  --cat-skills:   #fb923c;
  --cat-core:     #f472b6;
  --cat-gui:      #22d3ee;
  --cat-phal:     #facc15;
  --cat-other:    #94a3b8;
  --deprecated:   #f59e0b;
}

/* ---- Beta Banner ---- */
#beta-banner {
  position: fixed; top: var(--header-h); left: 0; right: 0; z-index: 90;
  background: linear-gradient(90deg, rgba(245,158,11,0.15), rgba(245,158,11,0.08));
  border-bottom: 1px solid rgba(245,158,11,0.3);
  padding: 6px 20px;
  display: flex; align-items: center; gap: 10px;
  font-size: 0.75rem; color: #fbbf24;
}
#beta-banner .beta-badge {
  background: rgba(245,158,11,0.2); border: 1px solid rgba(245,158,11,0.4);
  border-radius: 4px; padding: 1px 6px;
  font-weight: 700; letter-spacing: .05em; font-size: 0.65rem;
  flex-shrink: 0;
}
#beta-banner .beta-text { color: #d1a93f; }
#beta-banner .beta-dismiss {
  margin-left: auto; background: none; border: none; color: #8b949e;
  cursor: pointer; font-size: 1rem; line-height: 1; padding: 2px 4px;
  border-radius: 4px; transition: color .15s;
}
#beta-banner .beta-dismiss:hover { color: var(--text); }

/* ---- Header ---- */
#header {
  position: fixed; top: 0; left: 0; right: 0; z-index: 100;
  height: var(--header-h);
  background: rgba(13,17,23,0.95);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 16px;
  padding: 0 20px;
}
.logo {
  display: flex; align-items: center; gap: 10px;
  white-space: nowrap;
}
.logo-icon { font-size: 1.4rem; }
.logo-text { font-weight: 700; font-size: 1rem; color: #e6edf3; }
.logo-sub  { font-size: 0.7rem; color: var(--text-muted); margin-top: 1px; }

.search-wrap {
  position: relative; flex: 1; max-width: 640px;
  display: flex; align-items: center;
}
.search-wrap svg {
  position: absolute; left: 10px;
  width: 16px; height: 16px; color: var(--text-muted);
  pointer-events: none;
}
#search {
  width: 100%; padding: 7px 36px 7px 34px;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--text);
  font-family: inherit; font-size: 0.875rem;
  outline: none; transition: border-color .15s;
}
#search:focus { border-color: var(--accent); }
#search::placeholder { color: var(--text-dim); }
.search-kbd {
  position: absolute; right: 10px;
  font-size: 0.65rem; color: var(--text-dim);
  border: 1px solid var(--border); border-radius: 4px;
  padding: 1px 5px; font-family: inherit;
}

.header-right { display: flex; align-items: center; gap: 14px; white-space: nowrap; }
#stats { font-size: 0.75rem; color: var(--text-muted); }
.gh-link {
  font-size: 0.8rem; color: var(--text-muted);
  text-decoration: none; padding: 5px 10px;
  border: 1px solid var(--border); border-radius: var(--radius);
  transition: border-color .15s, color .15s;
}
.gh-link:hover { border-color: var(--accent); color: var(--accent); }

/* ---- Layout ---- */
.layout {
  display: flex;
  padding-top: var(--header-h);
  min-height: 100vh;
}
.layout.banner-visible { padding-top: calc(var(--header-h) + 33px); }

/* ---- Sidebar ---- */
#sidebar {
  position: fixed;
  top: var(--header-h); bottom: 0; left: 0;
  width: var(--sidebar-w);
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding-bottom: 32px;
  transition: top .15s;
}
#sidebar.banner-visible { top: calc(var(--header-h) + 33px); }
#sidebar::-webkit-scrollbar { width: 4px; }
#sidebar::-webkit-scrollbar-track { background: transparent; }
#sidebar::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.sidebar-all {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px 8px;
  font-size: 0.7rem; text-transform: uppercase; letter-spacing: .08em;
  color: var(--text-dim); font-weight: 600;
}
.sidebar-clear {
  font-size: 0.7rem; background: none; border: 1px solid var(--border);
  border-radius: 4px; color: var(--text-muted); padding: 2px 7px;
  cursor: pointer; transition: all .15s;
}
.sidebar-clear:hover { border-color: var(--accent); color: var(--accent); }

.cat-group { }
.cat-header {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 16px 5px;
  cursor: pointer; user-select: none;
  font-size: 0.78rem; font-weight: 600; color: var(--text-muted);
  transition: color .15s;
}
.cat-header:hover { color: var(--text); }
.cat-dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0;
}
.cat-count {
  margin-left: auto; font-size: 0.65rem;
  background: var(--surface2); border-radius: 10px;
  padding: 1px 6px; color: var(--text-dim);
}
.cat-items { padding-bottom: 4px; }
.sub-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 4px 16px 4px 32px;
  font-size: 0.775rem; color: var(--text-muted);
  cursor: pointer; border-left: 2px solid transparent;
  margin-left: 14px; transition: all .12s;
}
.sub-item:hover { color: var(--text); background: var(--surface2); }
.sub-item.active {
  color: var(--text);
  background: rgba(88,166,255,0.08);
}
.sub-item.active.colored { border-left-color: var(--item-color); }
.sub-count {
  font-size: 0.65rem; color: var(--text-dim);
}
.sub-item .depr-icon {
  font-size: 0.7rem; margin-left: 4px; color: var(--deprecated);
  flex-shrink: 0;
}

/* ---- Main ---- */
#main {
  flex: 1;
  margin-left: var(--sidebar-w);
  padding: 24px 28px 48px;
}

/* ---- Toolbar ---- */
#toolbar {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 16px;
}
#result-count { font-size: 0.8rem; color: var(--text-muted); }
.view-btns { display: flex; gap: 4px; margin-left: auto; }
.view-btn {
  padding: 4px 10px; font-size: 0.75rem;
  background: none; border: 1px solid var(--border);
  border-radius: 4px; color: var(--text-muted);
  cursor: pointer; transition: all .12s;
}
.view-btn.active { border-color: var(--accent); color: var(--accent); background: rgba(88,166,255,.08); }

/* ---- Cards grid ---- */
#cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(540px, 1fr));
  gap: 14px;
}
#cards-grid.list-view { grid-template-columns: 1fr; }

/* ---- Card ---- */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  transition: border-color .15s, box-shadow .15s;
  scroll-margin-top: calc(var(--header-h) + 16px);
}
.card:hover { border-color: #484f58; box-shadow: 0 4px 24px rgba(0,0,0,.3); }
.card:target { border-color: var(--accent); }
.card.deprecated { border-color: rgba(245,158,11,0.25); }
.card.deprecated:hover { border-color: rgba(245,158,11,0.5); }
.card.beta { border-color: rgba(99,102,241,0.25); }
.card.beta:hover { border-color: rgba(99,102,241,0.5); }
.card.legacy { border-color: rgba(148,163,184,0.2); }
.card.legacy:hover { border-color: rgba(148,163,184,0.4); }

.card-header {
  padding: 14px 16px 12px;
  border-left: 3px solid var(--card-color, var(--border));
}
.card.deprecated .card-header { border-left-color: var(--deprecated) !important; }
.card.beta .card-header { border-left-color: #818cf8 !important; }
.card.legacy .card-header { border-left-color: #64748b !important; }

.card-type-line {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.card-type {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem; font-weight: 600;
  color: #e6edf3;
  word-break: break-all;
}
.card-type.dynamic { color: var(--text-muted); font-style: italic; }
.copy-btn {
  font-size: 0.65rem; padding: 2px 6px;
  background: none; border: 1px solid var(--border);
  border-radius: 4px; color: var(--text-dim);
  cursor: pointer; flex-shrink: 0;
  transition: all .12s; font-family: inherit;
}
.copy-btn:hover { border-color: var(--accent); color: var(--accent); }
.copy-btn.copied { border-color: #34d399; color: #34d399; }
.badge-deprecated {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 7px; font-size: 0.62rem; font-weight: 700;
  border-radius: 12px; letter-spacing: .04em;
  background: rgba(245,158,11,0.12); color: #f59e0b;
  border: 1px solid rgba(245,158,11,0.35);
  flex-shrink: 0;
}
.badge-beta {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 7px; font-size: 0.62rem; font-weight: 700;
  border-radius: 12px; letter-spacing: .04em;
  background: rgba(99,102,241,0.12); color: #818cf8;
  border: 1px solid rgba(99,102,241,0.35);
  flex-shrink: 0;
}
.badge-legacy {
  display: inline-flex; align-items: center; gap: 3px;
  padding: 2px 7px; font-size: 0.62rem; font-weight: 700;
  border-radius: 12px; letter-spacing: .04em;
  background: rgba(148,163,184,0.10); color: #94a3b8;
  border: 1px solid rgba(148,163,184,0.3);
  flex-shrink: 0;
}
.card-meta {
  display: flex; align-items: center; gap: 6px;
  margin-top: 6px; flex-wrap: wrap;
}
.tag {
  font-size: 0.65rem; font-weight: 600; padding: 2px 7px;
  border-radius: 12px; letter-spacing: .02em;
}
.tag-sub {
  font-size: 0.7rem; color: var(--text-muted);
}
.card-class {
  font-size: 0.68rem; color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  margin-left: auto;
}

.card-doc {
  padding: 0 16px 12px;
  font-size: 0.8rem; color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  line-height: 1.5;
}

/* ---- Field table ---- */
.card-fields { overflow-x: auto; }
.card-fields table {
  width: 100%; border-collapse: collapse;
  font-size: 0.775rem;
}
.card-fields th {
  padding: 7px 14px 6px;
  text-align: left; font-weight: 600; font-size: 0.65rem;
  text-transform: uppercase; letter-spacing: .06em;
  color: var(--text-dim); border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,.02);
  white-space: nowrap;
}
.card-fields td {
  padding: 6px 14px;
  border-bottom: 1px solid rgba(48,54,61,.6);
  vertical-align: top; line-height: 1.45;
}
.card-fields tr:last-child td { border-bottom: none; }
.card-fields tr:hover td { background: rgba(255,255,255,.02); }
.field-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 500; color: #e6edf3; white-space: nowrap;
}
.field-type {
  font-family: 'JetBrains Mono', monospace;
  color: var(--accent); white-space: nowrap;
}
.field-name.extra, .field-type.extra { color: var(--text-dim); font-style: italic; }
.badge-req {
  display: inline-block; padding: 1px 5px;
  font-size: 0.6rem; font-weight: 700; letter-spacing: .04em;
  border-radius: 4px; white-space: nowrap;
  background: rgba(248,81,73,.15); color: #f85149;
  border: 1px solid rgba(248,81,73,.3);
}
.badge-opt {
  display: inline-block; padding: 1px 5px;
  font-size: 0.6rem; font-weight: 600; letter-spacing: .04em;
  border-radius: 4px; white-space: nowrap;
  color: var(--text-dim); border: 1px solid var(--border);
}
.field-default {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem; color: var(--text-dim); white-space: nowrap;
}
.field-desc { color: var(--text-muted); max-width: 320px; }

.card-nodata {
  padding: 10px 16px;
  font-size: 0.78rem; color: var(--text-dim); font-style: italic;
}

/* ---- Empty state ---- */
#empty-state {
  text-align: center; padding: 80px 20px;
  color: var(--text-muted);
}
#empty-state p { font-size: 1rem; margin-bottom: 8px; }
#empty-state small { font-size: 0.8rem; color: var(--text-dim); }

/* ---- Toast ---- */
#toast {
  position: fixed; bottom: 20px; right: 20px;
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 8px 14px;
  font-size: 0.8rem; color: var(--text);
  opacity: 0; transform: translateY(8px);
  transition: all .2s; pointer-events: none;
  z-index: 200;
}
#toast.show { opacity: 1; transform: translateY(0); }

/* ---- Scrollbar ---- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

/* ---- Responsive ---- */
@media (max-width: 900px) {
  #sidebar { display: none; }
  #main { margin-left: 0; padding: 16px 14px 40px; }
  #cards-grid { grid-template-columns: 1fr; }
  .logo-sub { display: none; }
  .header-right .gh-link { display: none; }
}
</style>
</head>
<body>

<!-- Beta Banner -->
<div id="beta-banner">
  <span class="beta-badge">BETA</span>
  <span class="beta-text">
    This reference is under active review. Message models are semi-automatically generated from source code and may be incomplete, inaccurate, or subject to change.
    Some subsystems are deprecated but documented here for historical reference —
    they are marked with <strong>⚠ deprecated</strong> badges.
    Do not rely on this page as an authoritative API contract.
  </span>
  <button class="beta-dismiss" id="dismiss-banner" title="Dismiss">✕</button>
</div>

<!-- Header -->
<header id="header">
  <div class="logo">
    <span class="logo-icon">🔊</span>
    <div>
      <div class="logo-text">OVOS MessageBus</div>
      <div class="logo-sub">Protocol Reference</div>
    </div>
  </div>
  <div class="search-wrap">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
      <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
    </svg>
    <input id="search" type="text" placeholder="Search message types, fields, subsystems…" autocomplete="off" spellcheck="false">
    <kbd class="search-kbd">/</kbd>
  </div>
  <div class="header-right">
    <span id="stats"></span>
    <a class="gh-link" href="https://github.com/OpenVoiceOS/ovos-pydantic-models" target="_blank" rel="noopener">
      GitHub ↗
    </a>
  </div>
</header>

<!-- Layout -->
<div class="layout banner-visible" id="layout">
  <aside id="sidebar" class="banner-visible">
    <div class="sidebar-all">
      <span>Subsystems</span>
      <button class="sidebar-clear" id="clear-filter">All</button>
    </div>
    <div id="sidebar-nav"></div>
  </aside>

  <main id="main">
    <div id="toolbar">
      <span id="result-count"></span>
      <div class="view-btns">
        <button class="view-btn active" id="btn-grid">Grid</button>
        <button class="view-btn" id="btn-list">List</button>
      </div>
    </div>
    <div id="cards-grid"></div>
    <div id="empty-state" style="display:none">
      <p>No messages match your search.</p>
      <small>Try a different query or clear the filter.</small>
    </div>
  </main>
</div>

<div id="toast"></div>

<script>
// ---- Data ----
const MESSAGES = __JSON_DATA__;

// Which subsystems are fully deprecated
const DEPRECATED_SUBSYSTEMS = new Set(__DEPRECATED_SUBSYSTEMS__);
// Which subsystems are beta / pre-release
const BETA_SUBSYSTEMS = new Set(__BETA_SUBSYSTEMS__);
// Which subsystems are legacy (functional but superseded)
const LEGACY_SUBSYSTEMS = new Set(__LEGACY_SUBSYSTEMS__);

// ---- Category config ----
const CAT_COLORS = {
  Audio:    '#a78bfa',
  OCP:      '#f43f5e',
  Listener: '#60a5fa',
  Intents:  '#34d399',
  Skills:   '#fb923c',
  Core:     '#f472b6',
  GUI:      '#22d3ee',
  PHAL:     '#facc15',
  Other:    '#94a3b8',
};

// ---- State ----
let activeCategory = null;
let activeSubsystem = null;
let searchQuery = '';
let viewMode = 'grid';

// ---- Beta banner dismiss ----
document.getElementById('dismiss-banner').addEventListener('click', () => {
  const banner = document.getElementById('beta-banner');
  const layout = document.getElementById('layout');
  const sidebar = document.getElementById('sidebar');
  banner.style.display = 'none';
  layout.classList.remove('banner-visible');
  sidebar.classList.remove('banner-visible');
});

// ---- Build sidebar ----
function buildSidebar() {
  const nav = document.getElementById('sidebar-nav');
  const byCategory = {};

  MESSAGES.forEach(m => {
    if (!byCategory[m.category]) byCategory[m.category] = {};
    const subs = byCategory[m.category];
    subs[m.subsystem] = (subs[m.subsystem] || 0) + 1;
  });

  const catOrder = ['Audio','OCP','Listener','Intents','Skills','Core','GUI','PHAL','Other'];
  let html = '';

  catOrder.forEach(cat => {
    const subs = byCategory[cat];
    if (!subs) return;
    const color = CAT_COLORS[cat] || '#94a3b8';
    const total = Object.values(subs).reduce((a,b) => a+b, 0);
    html += `<div class="cat-group" data-cat="${cat}">`;
    html += `<div class="cat-header" onclick="filterCat('${cat}')">
      <span class="cat-dot" style="background:${color}"></span>
      <span>${cat}</span>
      <span class="cat-count">${total}</span>
    </div>`;
    html += `<div class="cat-items">`;
    Object.entries(subs).sort((a,b) => a[0].localeCompare(b[0])).forEach(([sub, count]) => {
      const isDeprSub = MESSAGES.some(m => m.subsystem === sub && m.deprecated);
      const isBetaSub = !isDeprSub && MESSAGES.some(m => m.subsystem === sub && m.beta);
      const isLegacySub = !isDeprSub && !isBetaSub && MESSAGES.some(m => m.subsystem === sub && m.legacy);
      const deprIcon = isDeprSub ? `<span class="depr-icon" style="color:var(--deprecated)" title="Deprecated subsystem">⚠</span>` : '';
      const betaIcon = isBetaSub ? `<span class="depr-icon" style="color:#818cf8" title="Beta / pre-release subsystem">β</span>` : '';
      const legacyIcon = isLegacySub ? `<span class="depr-icon" style="color:#64748b" title="Legacy — functional but superseded">↩</span>` : '';
      html += `<div class="sub-item colored" data-sub="${sub}" style="--item-color:${color}"
                   onclick="filterSub('${cat}','${sub}')">${sub}${deprIcon}${betaIcon}${legacyIcon}<span class="sub-count">${count}</span></div>`;
    });
    html += `</div></div>`;
  });

  nav.innerHTML = html;
}

function filterCat(cat) {
  activeCategory = cat;
  activeSubsystem = null;
  render();
  updateSidebarActive();
}
function filterSub(cat, sub) {
  activeCategory = cat;
  activeSubsystem = sub;
  render();
  updateSidebarActive();
}
function clearFilter() {
  activeCategory = null;
  activeSubsystem = null;
  render();
  updateSidebarActive();
}
function updateSidebarActive() {
  document.querySelectorAll('.sub-item').forEach(el => {
    el.classList.toggle('active', el.dataset.sub === activeSubsystem);
  });
}

// ---- Search ----
let debounceTimer;
document.getElementById('search').addEventListener('input', e => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    searchQuery = e.target.value.trim().toLowerCase();
    render();
  }, 80);
});

document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== document.getElementById('search')) {
    e.preventDefault();
    document.getElementById('search').focus();
  }
  if (e.key === 'Escape') {
    document.getElementById('search').blur();
    clearFilter();
  }
});

document.getElementById('clear-filter').addEventListener('click', clearFilter);

// ---- View toggle ----
document.getElementById('btn-grid').addEventListener('click', () => setView('grid'));
document.getElementById('btn-list').addEventListener('click', () => setView('list'));
function setView(mode) {
  viewMode = mode;
  document.getElementById('cards-grid').classList.toggle('list-view', mode === 'list');
  document.getElementById('btn-grid').classList.toggle('active', mode === 'grid');
  document.getElementById('btn-list').classList.toggle('active', mode === 'list');
}

// ---- Filter + render ----
function matchesSearch(m, q) {
  if (!q) return true;
  const haystack = [
    m.message_type, m.class_name, m.category, m.subsystem, m.module, m.docstring,
    ...m.data_fields.map(f => f.name + ' ' + f.type + ' ' + f.description)
  ].join(' ').toLowerCase();
  return q.split(' ').every(token => haystack.includes(token));
}

function render() {
  const grid = document.getElementById('cards-grid');
  const empty = document.getElementById('empty-state');

  const visible = MESSAGES.filter(m => {
    if (activeSubsystem && m.subsystem !== activeSubsystem) return false;
    if (activeCategory && !activeSubsystem && m.category !== activeCategory) return false;
    return matchesSearch(m, searchQuery);
  });

  document.getElementById('result-count').textContent =
    visible.length === MESSAGES.length
      ? `${MESSAGES.length} messages`
      : `${visible.length} of ${MESSAGES.length} messages`;

  document.getElementById('stats').textContent =
    `${MESSAGES.length} messages`;

  if (visible.length === 0) {
    grid.innerHTML = '';
    empty.style.display = '';
    return;
  }
  empty.style.display = 'none';
  grid.innerHTML = visible.map(renderCard).join('');
}

// ---- Card rendering ----
function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderCard(m) {
  const color = CAT_COLORS[m.category] || '#94a3b8';
  const isDynamic = m.is_dynamic;
  const isUnknownDynamic = isDynamic && m.message_type === '(dynamic)';
  const tagBg = color + '22';
  const deprClass = m.deprecated ? ' deprecated' : (m.beta ? ' beta' : (m.legacy ? ' legacy' : ''));
  const deprBadge = m.deprecated
    ? `<span class="badge-deprecated">⚠ deprecated</span>`
    : (m.beta ? `<span class="badge-beta">β beta</span>`
    : (m.legacy ? `<span class="badge-legacy">↩ legacy</span>` : ''));

  // For dynamic message types show the format pattern (e.g. {skill_id}.intent) in
  // italic monospace; for fully unknown dynamics show a muted placeholder.
  const typeDisplay = isUnknownDynamic
    ? `<span class="card-type dynamic" title="Message type is computed at runtime">(dynamic)</span>`
    : isDynamic
      ? `<span class="card-type dynamic" title="Format pattern — actual type is computed at runtime">${esc(m.message_type)}</span>
         <span style="font-size:0.6rem;color:var(--text-dim);margin-left:2px;font-style:italic">format</span>`
      : `<span class="card-type">${esc(m.message_type)}</span>
         <button class="copy-btn" data-type="${esc(m.message_type)}">copy</button>`;

  const fieldsHtml = m.data_fields.length > 0 ? `
    <div class="card-fields">
      <table>
        <thead><tr>
          <th>Field</th><th>Type</th><th></th><th>Default</th><th>Description</th>
        </tr></thead>
        <tbody>
          ${m.data_fields.map(f => {
            const isExtra = f.name === '…';
            return `<tr>
              <td class="field-name${isExtra?' extra':''}">${esc(f.name)}</td>
              <td class="field-type${isExtra?' extra':''}">${esc(f.type)}</td>
              <td>${f.required && !isExtra ? '<span class="badge-req">req</span>' : (!isExtra ? '<span class="badge-opt">opt</span>' : '')}</td>
              <td class="field-default">${f.default ? esc(f.default) : ''}</td>
              <td class="field-desc">${esc(f.description)}</td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    </div>
  ` : `<div class="card-nodata">No typed data payload</div>`;

  return `
    <div class="card${deprClass}" id="${esc(m.id)}" style="--card-color:${color}">
      <div class="card-header">
        <div class="card-type-line">
          ${typeDisplay}
          ${deprBadge}
        </div>
        <div class="card-meta">
          <span class="tag" style="background:${tagBg};color:${color}">${esc(m.category)}</span>
          <span class="tag-sub">${esc(m.subsystem)}</span>
          <span class="card-class">${esc(m.class_name)}</span>
        </div>
      </div>
      ${m.docstring ? `<div class="card-doc">${esc(m.docstring)}</div>` : ''}
      ${fieldsHtml}
    </div>
  `;
}

// ---- Copy to clipboard ----
document.getElementById('cards-grid').addEventListener('click', e => {
  const btn = e.target.closest('.copy-btn');
  if (!btn) return;
  const text = btn.dataset.type;
  navigator.clipboard.writeText(text).then(() => {
    btn.textContent = '✓';
    btn.classList.add('copied');
    showToast(`Copied: ${text}`);
    setTimeout(() => { btn.textContent = 'copy'; btn.classList.remove('copied'); }, 1800);
  });
});

// ---- Toast ----
let toastTimer;
function showToast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2000);
}

// ---- URL hash deep-link ----
function handleHash() {
  const id = location.hash.slice(1);
  if (id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

// ---- Init ----
buildSidebar();
render();
window.addEventListener('hashchange', handleHash);
if (location.hash) setTimeout(handleHash, 100);
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

def generate(output_dir: str = "site") -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    print("Collecting message classes…", file=sys.stderr)
    messages = collect_messages()
    print(f"  Found {len(messages)} message classes", file=sys.stderr)

    json_data = json.dumps(messages, ensure_ascii=False, indent=None)
    deprecated_json = json.dumps(sorted(DEPRECATED_SUBSYSTEMS))
    beta_json = json.dumps(sorted(BETA_SUBSYSTEMS))
    legacy_json = json.dumps(sorted(LEGACY_SUBSYSTEMS))

    html = HTML_TEMPLATE.replace("__JSON_DATA__", json_data)
    html = html.replace("__DEPRECATED_SUBSYSTEMS__", deprecated_json)
    html = html.replace("__BETA_SUBSYSTEMS__", beta_json)
    html = html.replace("__LEGACY_SUBSYSTEMS__", legacy_json)

    index = out / "index.html"
    index.write_text(html, encoding="utf-8")

    size_kb = index.stat().st_size / 1024
    print(f"  Written: {index}  ({size_kb:.0f} KB)", file=sys.stderr)

    # Also write a minimal CNAME stub and _config.yml for GitHub Pages
    (out / ".nojekyll").write_text("", encoding="utf-8")

    print("Done. To serve locally:", file=sys.stderr)
    print(f"  python -m http.server 8080 --directory {output_dir}", file=sys.stderr)


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "site"
    generate(output)
