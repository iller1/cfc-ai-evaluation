from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
OUT_ROOT = REPO_ROOT / "dist_ux_v1_1"
PKG_DIR = OUT_ROOT / "CFC_DEMONSTRATOR_v1.1_UX_CANDIDATE"
ZIP_PATH = OUT_ROOT / "CFC_DEMONSTRATOR_v1.1_UX_CANDIDATE.zip"

EXCLUDE_TOP = {"runtime", "__pycache__"}
EXCLUDE_FILES = {"SHA256SUMS.txt"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def should_copy(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.parts and rel.parts[0] in EXCLUDE_TOP:
        return False
    if path.name in EXCLUDE_FILES:
        return False
    if "__pycache__" in rel.parts:
        return False
    return path.is_file()


def main() -> None:
    if OUT_ROOT.exists():
        shutil.rmtree(OUT_ROOT)
    PKG_DIR.mkdir(parents=True)

    for src in sorted(ROOT.rglob("*")):
        if not should_copy(src):
            continue
        rel = src.relative_to(ROOT)
        dst = PKG_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    metadata = {
        "artifact": "CFC_DEMONSTRATOR_v1.1_UX_CANDIDATE",
        "status": "UX_CANDIDATE_NOT_PROMOTED",
        "base_demonstrator": "v1.0 released historical baseline",
        "execution_engine": "cfc-anchor 0.2.90rc1",
        "wheel_sha256": "b3b1f11e060289afa4e7da61072f2c31be7f0da1786be90682ec307d4e1f5303",
        "ux_scope": [
            "new default 60-second landing",
            "five bounded human explanations",
            "five-case CLI path",
            "frozen first-impression protocol"
        ],
        "explicit_non_changes": [
            "no controller modification",
            "no case-runner modification",
            "no reference-execution modification",
            "no Operator Wrapper modification"
        ]
    }
    (PKG_DIR / "UX_CANDIDATE_METADATA.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )

    manifest = []
    for p in sorted(PKG_DIR.rglob("*")):
        if p.is_file() and p.name != "SHA256SUMS.txt":
            manifest.append(f"{sha256(p)}  {p.relative_to(PKG_DIR).as_posix()}")
    (PKG_DIR / "SHA256SUMS.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(PKG_DIR.rglob("*")):
            if p.is_file():
                zf.write(p, f"{PKG_DIR.name}/{p.relative_to(PKG_DIR).as_posix()}")

    summary = {
        "package_dir": PKG_DIR.name,
        "files_in_manifest": len(manifest),
        "zip_name": ZIP_PATH.name,
        "zip_sha256": sha256(ZIP_PATH),
    }
    (OUT_ROOT / "PACKAGE_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
