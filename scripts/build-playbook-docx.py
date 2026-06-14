#!/usr/bin/env python3
"""Convert the OTA playbook markdown to a Word doc with clickable links."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import pypandoc

REPO_BASE = "https://github.com/maiagordon-commits/PRD-Cross-Project/blob/main"
ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD = ROOT / "docs/playbooks/OTA-Financial-Data-Mapping-Playbook.md"
OUTPUT_DOCX = ROOT / "docs/playbooks/OTA-Financial-Data-Mapping-Playbook.docx"


def slugify_heading(line: str) -> str | None:
    match = re.match(r"^##\s+(.+)$", line.strip())
    if not match:
        return None
    text = match.group(1).strip()
    if "{#" in text:
        return None
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug).strip("-")
    return slug


def add_heading_ids(content: str) -> str:
    lines = []
    for line in content.splitlines():
        slug = slugify_heading(line)
        if slug and not line.rstrip().endswith(f"{{#{slug}}}"):
            lines.append(f"{line.rstrip()} {{#{slug}}}")
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def rewrite_links(content: str) -> str:
    def replace_link(match: re.Match[str]) -> str:
        text, url = match.group(1), match.group(2)
        if url.startswith("../workshop-notes/"):
            path = "docs/workshop-notes/" + url.removeprefix("../workshop-notes/")
            url = f"{REPO_BASE}/{path}"
        elif url.startswith("docs/"):
            url = f"{REPO_BASE}/{url}"
        return f"[{text}]({url})"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, content)


def count_hyperlinks(docx_path: Path) -> int:
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    return xml.count('w:hyperlink')


def main() -> None:
    content = SOURCE_MD.read_text(encoding="utf-8")
    content = add_heading_ids(content)
    content = rewrite_links(content)

    pypandoc.convert_text(
        content,
        to="docx",
        format="markdown",
        outputfile=str(OUTPUT_DOCX),
        extra_args=["--standalone", "--from=markdown+pipe_tables+task_lists"],
    )

    links = count_hyperlinks(OUTPUT_DOCX)
    print(f"Created {OUTPUT_DOCX}")
    print(f"Hyperlinks in document: {links}")


if __name__ == "__main__":
    main()
