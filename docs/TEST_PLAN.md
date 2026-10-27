# Test plan

| Scenario | Action | Expected |
|---|---|---|
| Exact original | Issue a file then verify identical bytes with same ID | VERIFIED |
| Altered file | Change content and verify using same ID | TAMPERED |
| Unknown ID | Verify unregistered ID | NOT_FOUND |
| Revoked | Revoke active ID then verify original | REVOKED |
| Duplicate issue | Register same ID twice | HTTP 409 |
| Unsupported extension | Upload unsupported file | HTTP 400 |
| Text PDF | Upload text PDF | PDF text extraction |
| Image OCR | Upload legible JPG/PNG with Tesseract installed | OCR extraction attempt |

The system must never mark metadata-only similarity as VERIFIED.
