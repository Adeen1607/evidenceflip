"""Import researcher-owned UTF-8 notes with explicit attribution and SHA-256."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re


def register_source(root: str | Path, file: str | Path, source_id: str, *,
                    title: str, origin: str, license: str) -> dict:
    """Copy an allowed .md/.txt document into sources/imported and update registry.

    The caller must have rights to register the document. The registry records
    caller-supplied origin and license metadata; it does not verify permission.
    """
    base = Path(root).resolve()
    original = Path(file).expanduser().resolve()
    if not original.is_file() or original.suffix.lower() not in {".md", ".txt"}:
        raise ValueError("Input must be an existing .md or .txt file")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", source_id):
        raise ValueError("Source ID must contain lowercase letters, digits, dot, underscore or hyphen")
    if any(not isinstance(x, str) or not x.strip() for x in (title, origin, license)):
        raise ValueError("Title, provenance/origin and license must be declared")
    data = original.read_bytes()
    if len(data) > 2_000_000:
        raise ValueError("Source exceeds 2 MB size limit")
    content = data.decode("utf-8")
    if not content.strip() or "\x00" in content:
        raise ValueError("Source must contain nonempty UTF-8 text")
    manifest = base / "sources" / "manifest.json"
    if not manifest.is_file():
        raise ValueError("No sources/manifest.json in repository root")
    registry = json.loads(manifest.read_text(encoding="utf-8"))
    if any(row.get("id") == source_id for row in registry["sources"]):
        raise ValueError("Source ID already registered")
    target = (base / "sources" / "imported" / (source_id + original.suffix.lower())).resolve()
    if not target.is_relative_to(base) or target.exists():
        raise ValueError("Unsafe or existing destination")
    target.parent.mkdir(parents=True, exist_ok=True)
    relative = target.relative_to(base).as_posix()
    entry = {"id": source_id, "title": title, "path": relative, "type": "research-note",
             "origin": origin, "license": license, "sha256": hashlib.sha256(data).hexdigest()}
    temp_manifest = manifest.with_name("manifest.json.tmp")
    if temp_manifest.exists():
        raise ValueError("Temporary registry file exists; resolve pending concurrent import")
    with target.open("xb") as out:
        out.write(data)
    try:
        registry["sources"].append(entry)
        with temp_manifest.open("x", encoding="utf-8") as out:
            json.dump(registry, out, indent=2)
            out.write("\n")
        os.replace(temp_manifest, manifest)
    except Exception:
        target.unlink(missing_ok=True)
        temp_manifest.unlink(missing_ok=True)
        raise
    return entry
