# Pro Beta PDF/DOCX document preview — scoped implementation

This is NOT automatic document verification by CFC.

## Implemented in this candidate
- A conversation-owned and bearer-authenticated POST `/api/conversations/{conversation_id}/extract-document`. Authorization is checked *before* base64 decode and parser invocation.
- JSON/base64 transport size capped before the general HTTP body reader; decoded raw document maximum 2 MiB.
- File extension **and** PDF/DOCX signature checked; a user cannot simply rename a different format to bypass detection.
- Ephemeral text extraction runs in a separate child process with CPU, memory, output and wall-time limits. No binary file is written to storage; no user document bytes are included in error messages or application logs.
- PDF: strict parsing, maximum 10 pages, page content stream bound, no OCR for image-only/scanned PDFs, reject encrypted PDFs.
- DOCX: reject encrypted/duplicate/path traversal/symlink/unsupported ZIP members; compressed/expanded byte count, ratio and entry count limits; parse main document XML with defusedxml, not archive extraction to disk.
- Return extracted text (maximum 40,000 chars), SHA-256 of original bytes, type, optional page count, explicit `EXTRACTED_TEXT_UNVERIFIED` and `USER_REVIEW_REQUIRED_NOT_CFC_EVIDENCE`.
- Browser displays extracted text and requires explicit checkbox confirmation before a user may send it to an AI provider; the existing chat route stores the resulting **text message**. No raw uploaded document store.
- Switching workspace/conversation and removing the file clears browser-held pending text. Errors preserve the user's typed prompt and do not send source text automatically.

## Explicit limitations
- Untrusted PDF/DOCX can remain dangerous despite parser limits; this is a bounded pilot implementation, not a hardened multi-tenant malware processing service.
- No OCR, no document fidelity guarantee, no image/table semantic reconstruction, no encrypted file handling, and no legal/compliance assurance.
- The selected model can read the extracted text only after human confirmation and explicit send. The extracted content is *untrusted source data*, not an instruction or verified provenance.
- A user's own mapping of explicit structured HAWM fields is still required for CFC. No free-text/attachment-to-CFC inference, certificate of independent source, or automatic VERIFIED status.
- For real third-party pilots, add operational security controls (malware scanning/isolated low-privilege parser runtime, quotas, retention notice, privacy review, file-specific audit of hashes and mappings) before enabling broad external document upload.
