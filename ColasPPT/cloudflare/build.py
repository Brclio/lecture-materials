"""Package the self-contained lecture for Cloudflare Pages."""

import hashlib
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent
LECTURE = HERE.parent / "厦门工学院·AI浪潮下，如何学习与创造.html"
OUTPUT = HERE.parent / "_work" / "cloudflare-pages"
PART_BYTES = 16 * 1024 * 1024


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=OUTPUT.parent) as staging:
        site = Path(staging) / "site"
        parts_dir = site / "parts"
        parts_dir.mkdir(parents=True)
        parts = []
        digest = hashlib.sha256()
        size = 0
        with LECTURE.open("rb") as source:
            while True:
                chunk = source.read(PART_BYTES)
                if not chunk:
                    break
                digest.update(chunk)
                size += len(chunk)
                filename = hashlib.sha256(chunk).hexdigest() + ".bin"
                (parts_dir / filename).write_bytes(chunk)
                parts.append("/parts/" + filename)

        if not parts:
            raise ValueError("The lecture is empty")
        lecture = dict(path="/" + LECTURE.name, parts=parts, sha256=digest.hexdigest(), size=size)
        worker = (HERE / "worker.js").read_text(encoding="utf-8")
        (site / "_worker.js").write_text(
            "const lecture = " + json.dumps(lecture, ensure_ascii=False) + ";\n\n" + worker,
            encoding="utf-8",
        )
        (site / "_routes.json").write_text(
            json.dumps({"version": 1, "include": ["/*"], "exclude": []}), encoding="utf-8"
        )
        if OUTPUT.exists():
            shutil.rmtree(OUTPUT)
        site.rename(OUTPUT)
    print(f"{size} bytes in {len(parts)} parts, SHA-256 {digest.hexdigest()}")


if __name__ == "__main__":
    build()
