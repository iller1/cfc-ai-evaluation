from __future__ import annotations

import base64
import io
import json
import unittest
import zipfile
from unittest.mock import patch

from pro_beta.document_extract import (
    DocumentError, MAX_DOCUMENT_BYTES, _decode_document_payload,
    extract_document_in_worker, extract_raw_document,
)
from pro_beta.api import APIError, ProBetaAPI
from pro_beta.auth_boundary import AuthBoundary, AuthenticationError, VerifiedExternalIdentity
from pro_beta.persistence import InMemoryPersistence
from pro_beta.service import ProBetaService
from pro_beta.contracts import UserAccount


def sample_docx(text="Potwierdzenie jakości, partia NW-0926"):
    body = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        b'<w:body><w:p><w:r><w:t>' + text.encode("utf-8") +
        b'</w:t></w:r></w:p></w:body></w:document>'
    )
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("word/document.xml", body)
    return out.getvalue()


def upload(filename, raw):
    return {"filename": filename, "content_base64": base64.b64encode(raw).decode("ascii")}


class ExtractorTests(unittest.TestCase):
    def test_valid_docx_extracts_text_without_persisting_binary(self):
        raw = sample_docx()
        result = extract_raw_document("report.docx", raw)
        self.assertIn("NW-0926", result["text"])
        self.assertEqual(result["status"], "EXTRACTED_TEXT_UNVERIFIED")
        self.assertFalse(result["persisted_document_bytes"])
        self.assertEqual(len(result["sha256"]), 64)

    def test_worker_round_trip_docx(self):
        result = extract_document_in_worker(upload("report.docx", sample_docx()))
        self.assertIn("NW-0926", result["text"])
        self.assertEqual(result["boundary"], "USER_REVIEW_REQUIRED_NOT_CFC_EVIDENCE")

    def test_reject_wrong_signatures_and_oversize(self):
        for filename, raw in [
            ("wrong.pdf", b"not a PDF"),
            ("wrong.docx", b"not a zip"),
            ("wrong.exe", sample_docx()),
        ]:
            with self.subTest(filename=filename), self.assertRaises(DocumentError):
                extract_raw_document(filename, raw)
        with self.assertRaises(DocumentError):
            _decode_document_payload(upload("report.pdf", b"x" * (MAX_DOCUMENT_BYTES + 1)))

    def test_reject_broken_base64(self):
        with self.assertRaises(DocumentError):
            _decode_document_payload({"filename": "report.pdf", "content_base64": "??not base64"})

    def test_reject_docx_zip_bomb_by_declared_size(self):
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", "<Types/>")
            z.writestr("word/document.xml", "A" * (5 * 1024 * 1024))
        with self.assertRaises(DocumentError):
            extract_raw_document("large.docx", out.getvalue())

    def test_reject_duplicate_archive_members(self):
        import warnings
        out = io.BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(out, "w") as z:
                z.writestr("[Content_Types].xml", "<Types/>")
                z.writestr("word/document.xml", "<x/>")
                z.writestr("word/document.xml", "<x/>")
        with self.assertRaisesRegex(DocumentError, "ZIP_STRUCTURE"):
            extract_raw_document("duplicate.docx", out.getvalue())

    def test_text_pdf_extracts_real_page_text(self):
        from pypdf import PdfWriter
        from pypdf.generic import (
            DecodedStreamObject, DictionaryObject, NameObject,
        )
        writer = PdfWriter()
        page = writer.add_blank_page(width=300, height=300)
        font = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({
                NameObject("/F1"): writer._add_object(font)
            })
        })
        stream = DecodedStreamObject()
        stream.set_data(b"BT /F1 12 Tf 20 20 Td (NW-0926 PDF text) Tj ET")
        page[NameObject("/Contents")] = writer._add_object(stream)
        output = io.BytesIO()
        writer.write(output)
        result = extract_document_in_worker(upload("report.pdf", output.getvalue()))
        self.assertEqual(result["kind"], "pdf")
        self.assertEqual(result["page_count"], 1)
        self.assertIn("NW-0926 PDF text", result["text"])
        self.assertEqual(result["status"], "EXTRACTED_TEXT_UNVERIFIED")

    def test_image_only_pdf_has_no_made_up_text(self):
        from pypdf import PdfWriter
        out = io.BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=300, height=300)
        writer.write(out)
        with self.assertRaisesRegex(DocumentError, "TEXT_NOT_FOUND"):
            extract_raw_document("blank.pdf", out.getvalue())


class Identity:
    def verify(self, token):
        if token not in ("a", "b"):
            raise AuthenticationError("CREDENTIAL_INVALID")
        return VerifiedExternalIdentity(
            subject="provider|" + token,
            issuer="https://identity.example/",
            audience="cfc-hawm-pro-beta",
            provider_verified=True,
        )


class ExtractionAuthTests(unittest.TestCase):
    def setUp(self):
        self.store = InMemoryPersistence()
        for letter in ("a", "b"):
            self.store.create_user(UserAccount(
                user_id="usr_" + letter,
                external_auth_subject="provider|" + letter,
                email=None,
            ))
        self.api = ProBetaAPI(
            verifier=Identity(),
            auth_boundary=AuthBoundary(
                self.store, expected_issuer="https://identity.example/",
                expected_audience="cfc-hawm-pro-beta",
            ),
            service=ProBetaService(self.store),
        )
        ws = self.api.create_workspace("a", {"name": "Test"})
        conversation = self.api.create_conversation("a", ws["workspace_id"], {"title": "Private"})
        self.cid = conversation["conversation_id"]

    def test_other_user_cannot_invoke_parser(self):
        with patch("pro_beta.document_extract.extract_document_in_worker") as worker:
            with self.assertRaises(APIError) as ctx:
                self.api.extract_document_preview("b", self.cid, upload("report.docx", sample_docx()))
            self.assertIn(ctx.exception.status, (403, 404))
            worker.assert_not_called()

    def test_missing_auth_does_not_parse(self):
        with patch("pro_beta.document_extract.extract_document_in_worker") as worker:
            with self.assertRaises(APIError) as ctx:
                self.api.extract_document_preview("", self.cid, upload("report.docx", sample_docx()))
            self.assertEqual(ctx.exception.status, 401)
            worker.assert_not_called()

    def test_owned_document_returns_preview_but_no_cfc_decision(self):
        result = self.api.extract_document_preview("a", self.cid, upload("report.docx", sample_docx()))
        self.assertIn("NW-0926", result["text"])
        self.assertNotIn("decision", result)
        self.assertNotIn("claim_state", result)
        self.assertFalse(result["persisted_document_bytes"])
