# Project Overview

## Problem
Employers receive forged educational documents; manual verification can be slow and inconsistent.

## Proposed solution
An authorized institution registers an original certificate in a trusted issuer registry. EduVerify computes SHA-256, extracts text via PDF parsing/OCR, and compares a recruiter's uploaded file with the issuer record.

## AI component
OCR with Tesseract for images, PDF text extraction with pypdf, and explainable rule-based entity extraction for student name, university, degree, year and credential ID. It is a baseline that can later be replaced by spaCy NER or a trained model. OCR is fallible and requires human review.

## Verification
VERIFIED means exact SHA-256 match and active issuer record. TAMPERED means supplied ID exists but hash differs. REVOKED means issuer revoked the record. NOT_FOUND means no matching issuer record. Metadata is supporting evidence, not a substitute for exact hash match.

## Trusted source
The institution is the authority. A credential is trusted only after an authorized issuer registers it. Current prototype simulates this with SQLite; no live blockchain is included in this AI-first edition.

## Future work
Issuer authentication, institution onboarding, advanced NER, multilingual OCR, human review, digital signatures, and a Polygon smart-contract registry adapter.
