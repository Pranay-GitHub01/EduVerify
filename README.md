# EduVerify — AI Certificate Verification (Windows)

A runnable final-year prototype using React + Vite, FastAPI, SQLite, PDF/OCR extraction, rule-based NLP field extraction, and SHA-256 document fingerprints.

## Features
- Issuer portal to register certificates (PDF, PNG, JPG, TXT).
- SHA-256 hash calculated from exact uploaded file bytes.
- PDF text extraction using pypdf; image OCR using Tesseract/pytesseract when installed.
- Rule-based entity extraction for student name, institution, degree, graduation year and credential ID.
- Recruiter verification with statuses VERIFIED, TAMPERED, REVOKED and NOT_FOUND.
- Credential registry, revoke function, dashboard counters, verification logs and synthetic demo seed.

> This selected AI-first edition uses a local SQLite trusted issuer registry. It does not claim blockchain integration. An authorized issuer registering an original record is the trust source. OCR assists extraction but does not prove authenticity.

## Requirements
Windows 10/11, Python 3.10+, Node.js 18+. For image OCR install Tesseract OCR for Windows and add its folder (commonly `C:\Program Files\Tesseract-OCR`) to PATH. Text-based PDFs work without Tesseract. Scanned PDFs need optional `pdf2image` plus Poppler as well.

## Start backend
```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
API docs: http://127.0.0.1:8000/docs

## Start frontend (second terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

## Demo
1. Click **Load synthetic demo record** on Overview, or issue your own certificate in Issue Credential.
2. To verify the seeded record, use `sample_certificates/valid_demo_certificate.txt` and ID `EV-DEMO-001`.
3. It should return VERIFIED. Use `sample_certificates/altered_demo_certificate.txt` with the same ID to get TAMPERED.
4. Revoke the credential from Registry and verify again to get REVOKED.

## Tests
```powershell
cd backend
python -m unittest discover -s tests -v
```

## Limitations and academic integrity
- OCR and regex extraction are a baseline AI/document-intelligence component; results need human review.
- Exact hash equality establishes byte-for-byte identity with the registered file, not the issuer's real-world legitimacy.
- Only authorized institutions should register credentials. This prototype has no production-grade login or institutional identity proof.
- Files are temporary during request processing; uploaded file copies are deleted after API processing.
- Demo dataset is synthetic. Do not upload real personal data into a public demo.
