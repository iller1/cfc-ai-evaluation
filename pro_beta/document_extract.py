"""Bounded, ephemeral text extraction for document previews; never evidence certification."""
from __future__ import annotations

import base64
import binascii
import hashlib
import io
import json
import os
import stat
import subprocess
import sys
import zipfile

MAX_DOCUMENT_BYTES = 2 * 1024 * 1024
MAX_TEXT_CHARS = 40000
MAX_PDF_PAGES = 10
MAX_ZIP_ENTRIES = 200
MAX_ZIP_UNCOMPRESSED = 8 * 1024 * 1024
MAX_ZIP_MEMBER = 4 * 1024 * 1024


class DocumentError(ValueError):
    """A stable, content-free failure code that may be shown to a user."""


def _kind(filename: str, raw: bytes) -> str:
    if not isinstance(filename, str) or not (0 < len(filename) <= 120):
        raise DocumentError("DOCUMENT_NAME_INVALID")
    name = filename.strip().lower()
    if name.endswith(".pdf") and raw.startswith(b"%PDF-"):
        return "pdf"
    if name.endswith(".docx") and raw.startswith(b"PK\x03\x04"):
        return "docx"
    raise DocumentError("DOCUMENT_TYPE_OR_SIGNATURE_UNSUPPORTED")


def _check_text(text: str) -> str:
    if not isinstance(text, str):
        raise DocumentError("DOCUMENT_TEXT_NOT_FOUND")
    text = text.replace("\x00", "").strip()
    if not text:
        raise DocumentError("DOCUMENT_TEXT_NOT_FOUND_OR_SCANNED")
    if len(text) > MAX_TEXT_CHARS:
        raise DocumentError("DOCUMENT_TEXT_TOO_LONG")
    return text


def _parse_docx(raw: bytes) -> tuple[str, int]:
    from defusedxml import ElementTree as SafeET

    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            entries = archive.infolist()
            names = [item.filename for item in entries]
            if not entries or len(entries) > MAX_ZIP_ENTRIES or len(names) != len(set(names)):
                raise DocumentError("DOCUMENT_ZIP_STRUCTURE_INVALID")
            total = 0
            for item in entries:
                name = item.filename
                if (
                    name.startswith("/") or "\\" in name
                    or ".." in name.split("/") or "\x00" in name
                    or stat.S_ISLNK(item.external_attr >> 16)
                    or item.flag_bits & 0x1
                    or item.compress_type not in (zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED)
                ):
                    raise DocumentError("DOCUMENT_ZIP_STRUCTURE_INVALID")
                if item.file_size > MAX_ZIP_MEMBER:
                    raise DocumentError("DOCUMENT_ZIP_SIZE_LIMIT")
                total += item.file_size
                if total > MAX_ZIP_UNCOMPRESSED:
                    raise DocumentError("DOCUMENT_ZIP_SIZE_LIMIT")
                if item.file_size and item.file_size > max(1, item.compress_size) * 100:
                    raise DocumentError("DOCUMENT_ZIP_RATIO_LIMIT")
            if "word/document.xml" not in names or "[Content_Types].xml" not in names:
                raise DocumentError("DOCUMENT_DOCX_PARTS_MISSING")
            document_xml = archive.read("word/document.xml")
            if len(document_xml) > MAX_ZIP_MEMBER:
                raise DocumentError("DOCUMENT_ZIP_SIZE_LIMIT")
    except (zipfile.BadZipFile, EOFError, OSError, RuntimeError, NotImplementedError) as exc:
        raise DocumentError("DOCUMENT_ZIP_PARSE_FAILED") from exc

    try:
        root = SafeET.fromstring(document_xml)
        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        paragraphs = []
        for paragraph in root.iter(ns + "p"):
            pieces = []
            for node in paragraph.iter():
                if node.tag == ns + "t" and node.text:
                    pieces.append(node.text)
                elif node.tag == ns + "tab":
                    pieces.append("\t")
                elif node.tag in (ns + "br", ns + "cr"):
                    pieces.append("\n")
            if pieces:
                paragraphs.append("".join(pieces))
            if len(paragraphs) > 20000:
                raise DocumentError("DOCUMENT_TEXT_TOO_LONG")
        return _check_text("\n".join(paragraphs)), 0
    except DocumentError:
        raise
    except Exception as exc:
        raise DocumentError("DOCUMENT_DOCX_XML_INVALID") from exc


def _parse_pdf(raw: bytes) -> tuple[str, int]:
    from pypdf import PdfReader

    try:
        reader = PdfReader(io.BytesIO(raw), strict=True)
        if reader.is_encrypted:
            raise DocumentError("DOCUMENT_PDF_ENCRYPTED")
        page_count = len(reader.pages)
        if not 1 <= page_count <= MAX_PDF_PAGES:
            raise DocumentError("DOCUMENT_PDF_PAGE_LIMIT")
        texts = []
        for page in reader.pages:
            content = page.get_contents()
            if content is not None and len(content.get_data()) > 1024 * 1024:
                raise DocumentError("DOCUMENT_PDF_CONTENT_STREAM_LIMIT")
            texts.append(page.extract_text() or "")
            if sum(len(part) for part in texts) > MAX_TEXT_CHARS:
                raise DocumentError("DOCUMENT_TEXT_TOO_LONG")
        return _check_text("\n\n".join(texts)), page_count
    except DocumentError:
        raise
    except Exception as exc:
        raise DocumentError("DOCUMENT_PDF_PARSE_FAILED") from exc


def extract_raw_document(filename: str, raw: bytes) -> dict:
    if not isinstance(raw, bytes) or not 0 < len(raw) <= MAX_DOCUMENT_BYTES:
        raise DocumentError("DOCUMENT_BYTE_LIMIT")
    kind = _kind(filename, raw)
    text, page_count = _parse_pdf(raw) if kind == "pdf" else _parse_docx(raw)
    return {
        "filename": filename,
        "kind": kind,
        "text": text,
        "character_count": len(text),
        "page_count": page_count if kind == "pdf" else None,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "status": "EXTRACTED_TEXT_UNVERIFIED",
        "boundary": "USER_REVIEW_REQUIRED_NOT_CFC_EVIDENCE",
        "persisted_document_bytes": False,
    }


def _decode_document_payload(payload: dict) -> tuple[str, bytes]:
    filename = payload.get("filename")
    value = payload.get("content_base64")
    if not isinstance(filename, str) or not isinstance(value, str):
        raise DocumentError("DOCUMENT_PAYLOAD_REQUIRED")
    if len(value) > (MAX_DOCUMENT_BYTES * 4 // 3) + 8:
        raise DocumentError("DOCUMENT_BYTE_LIMIT")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise DocumentError("DOCUMENT_BASE64_INVALID") from exc
    if not 0 < len(raw) <= MAX_DOCUMENT_BYTES:
        raise DocumentError("DOCUMENT_BYTE_LIMIT")
    _kind(filename, raw)
    return filename, raw


def extract_document_in_worker(payload: dict) -> dict:
    """No binary storage, stderr forwarding, or direct parser execution in HTTP thread."""
    filename, raw = _decode_document_payload(payload)
    request = json.dumps({
        "filename": filename, "content_base64": base64.b64encode(raw).decode("ascii")
    }).encode("utf-8")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pro_beta.document_extract_worker"],
            input=request, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=12, check=False,
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
            },
        )
    except subprocess.TimeoutExpired as exc:
        raise DocumentError("DOCUMENT_PARSE_TIMEOUT") from exc
    if result.returncode:
        raise DocumentError("DOCUMENT_PARSER_PROCESS_FAILED")
    try:
        response = json.loads(result.stdout.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise DocumentError("DOCUMENT_PARSER_RESPONSE_INVALID") from exc
    if not isinstance(response, dict):
        raise DocumentError("DOCUMENT_PARSER_RESPONSE_INVALID")
    if response.get("error"):
        raise DocumentError(str(response["error"]))
    if (response.get("status") != "EXTRACTED_TEXT_UNVERIFIED"
            or not isinstance(response.get("text"), str)
            or len(response["text"]) > MAX_TEXT_CHARS):
        raise DocumentError("DOCUMENT_PARSER_RESPONSE_INVALID")
    return response
