"""P77-A synthetic DOCX parser regression. Run: python -B test_p77_intake.py"""
import base64
import io
import unittest
import zipfile
import document_intake as d

NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

def parse_docx(xml, encoding="utf-8"):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", xml.encode(encoding))
    return d.parse({"mode": "file", "filename": "synthetic.docx",
                    "content_b64": base64.b64encode(stream.getvalue()).decode("ascii")})

class TestP77(unittest.TestCase):
    def test_valid(self):
        r = parse_docx(f'<w:document xmlns:w="{NS}"><w:body><w:p><w:r><w:t>Safe</w:t></w:r></w:p></w:body></w:document>')
        self.assertEqual(r["text"], "Safe")
        self.assertFalse(r["cfc_evaluated_document"])

    def test_false_positive_inside_border(self):
        xml = f'<w:document xmlns:w="{NS}"><w:body><w:p><w:pPr><w:pBdr><w:insideH/></w:pBdr></w:pPr><w:r><w:t>Safe</w:t></w:r></w:p></w:body></w:document>'
        self.assertEqual(parse_docx(xml)["text"], "Safe")

    def test_alternate_namespace_prefix_tracked_change(self):
        xml = f'<q:document xmlns:q="{NS}"><q:body><q:p><q:ins><q:r><q:t>Inserted</q:t></q:r></q:ins></q:p></q:body></q:document>'
        with self.assertRaisesRegex(d.IntakeRefused, "TRACKED_CHANGES"):
            parse_docx(xml)

    def test_utf16_dtd(self):
        xml = f'<?xml version="1.0" encoding="utf-16"?><!DOCTYPE w:document [<!ENTITY e "EXPANDED-ENTITY">]><w:document xmlns:w="{NS}"><w:body><w:p><w:r><w:t>&e;</w:t></w:r></w:p></w:body></w:document>'
        with self.assertRaisesRegex(d.IntakeRefused, "DOCX_XML_ENTITIES_REFUSED"):
            parse_docx(xml, "utf-16")

    def test_hidden(self):
        xml = f'<w:document xmlns:w="{NS}"><w:body><w:p><w:r><w:rPr><w:vanish/></w:rPr><w:t>Hidden</w:t></w:r></w:p></w:body></w:document>'
        with self.assertRaisesRegex(d.IntakeRefused, "HIDDEN_TEXT_DOCX_REFUSED"):
            parse_docx(xml)

    def test_paste(self):
        self.assertEqual(d.parse({"mode": "paste", "text": "Synthetic plain text"})["text"], "Synthetic plain text")

    def test_empty(self):
        with self.assertRaises(d.IntakeRefused):
            d.parse({"mode": "paste", "text": ""})

if __name__ == "__main__":
    unittest.main(verbosity=2)
