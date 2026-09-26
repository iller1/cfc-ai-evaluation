# Pro Beta — chat-first acceptance and attachment boundary

Status: scoped frontend change proposed for review. No deployment is implied.

## Primary layout
1. Conversation selection, question/answer history, composer.
2. Latest persisted CFC decision derived only from the controller presentation.
3. Latest HAWM **user working state**, plainly distinct from verified evidence.
4. Export of the complete technical Markdown audit report.
5. Collapsed-by-default provider keys, HAWM structured inputs, founding beta and benchmark tools.

Copy actions copy only message body, not message/provider metadata.

## Working attachment v1
- Exactly one UTF-8 TXT/MD attachment selected inside the chat composer.
- Display its name and byte size and provide removal before sending.
- Reject empty, wrong-extension, invalid UTF-8, NUL-containing, >64 KiB files or decoded content >50,000 chars. No binary server upload route and no server-side attachment store.
- Keep selected text in current browser memory until explicit user send/save. Include it as visibly bounded **untrusted source text** in the resulting chat message, which is persisted by the existing message/API route and sent to the selected external model if the user chooses an AI send action.
- Clear after success, explicit removal or conversation/workspace switch; preserve pending attachment after network/provider failure. When comparing all three models, the composed prompt (including the attachment) goes to all three.
- Ordinary model replies remain MODEL_REPLY_UNCHECKED / CFC NOT_CONNECTED_C2. Text extraction and storing a chat message do not certify its contents or feed them into CFC automatically.

## Deferred: safe PDF/DOCX support
Implement as a separate authenticated, owner-scoped document extraction feature after review of parsing isolation, content-based type checks, size/page/decompression limits, retention/deletion, attribution/provenance of extracted passages, hostile document instructions and explicit human confirmation of mapped structured evidence before frozen CFC. Do not show PDF or DOCX as a working option before implementation and tests.

The frontend must never infer independent sources from separate document filenames, mark arbitrary text verified, or present an AI answer as a CFC decision. A readable layperson export can be designed separately over persisted results without replacing the full audit export.
