import tempfile
import subprocess
from pathlib import Path
import os
import re


def sanitize_filename(filename: str, fallback: str = "chat") -> str:
    # Remove or replace non-ASCII characters, keep it simple and safe for HTTP headers
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
    return safe or fallback


def markdown_to_docx(markdown_content: str, timeout: int = 15) -> bytes:
    """
    Convert markdown content to docx using Pandoc.
    Returns the docx file as bytes, cleans up temp files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = Path(tmpdir) / "input.md"
        docx_path = Path(tmpdir) / "output.docx"
        md_path.write_text(markdown_content, encoding="utf-8")
        try:
            result = subprocess.run(
                ["pandoc", str(md_path), "-o", str(docx_path)],
                capture_output=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Pandoc failed: {result.stderr.decode('utf-8')}")
            docx_bytes = docx_path.read_bytes()
        finally:
            # Ensure files are deleted before returning
            if md_path.exists():
                try:
                    os.remove(md_path)
                except Exception:
                    pass
            if docx_path.exists():
                try:
                    os.remove(docx_path)
                except Exception:
                    pass
        return docx_bytes
