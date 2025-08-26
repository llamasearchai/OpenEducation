from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

from pypdf import PdfReader
from ..models.content_block import ContentBlock
from .pdf_utils import extract_chapters_from_pdf


class ContentSourceError(Exception):
    pass


@dataclass
class ContentSource:
    id: str
    path: str
    type: str

    def load_text(self) -> str:
        p = Path(self.path)
        if not p.exists():
            raise ContentSourceError(f"Missing source: {p}")
        if self.type == "markdown":
            text = p.read_text(encoding="utf-8")
            text = re.sub(r"```.*?```", "", text, flags=re.S)
            return text
        if self.type == "text":
            return p.read_text(encoding="utf-8")
        if self.type == "pdf":
            reader = PdfReader(str(p))
            return "\n\n".join([page.extract_text() or "" for page in reader.pages])
        if self.type == "json":
            return json.dumps(
                json.loads(p.read_text(encoding="utf-8")), ensure_ascii=False, indent=2
            )
        if self.type == "csv":
            return p.read_text(encoding="utf-8")
        raise ContentSourceError(f"Unsupported type: {self.type}")

    def to_blocks(self) -> List[ContentBlock]:
        if self.type == "pdf":
            return extract_chapters_from_pdf(self.path, self.id)

        text = self.load_text()
        chunks = []
        for part in re.split(r"\n\s*##+\s+", text):
            subparts = re.split(r"\n\n+", part)
            buf = []
            for sp in subparts:
                buf.append(sp.strip())
                if sum(len(x) for x in buf) > 800:
                    chunks.append("\n".join(buf))
                    buf = []
            if buf:
                chunks.append("\n".join(buf))
        blocks = []
        for ch in chunks:
            title = ch.split("\n", 1)[0][:80] if "\n" in ch else ch[:80]
            blocks.append(ContentBlock.from_text(title=title, text=ch, source_id=self.id))
        return blocks
