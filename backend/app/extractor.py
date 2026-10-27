from pathlib import Path
import re

def read_document(path: str):
    p = Path(path); ext = p.suffix.lower()
    if ext == '.txt': return p.read_text(encoding='utf-8', errors='ignore'), 'text'
    if ext == '.pdf':
        try:
            from pypdf import PdfReader
            text = '\n'.join(page.extract_text() or '' for page in PdfReader(str(p)).pages)
            if text.strip(): return text, 'pdf_text'
        except Exception: pass
        try:
            from pdf2image import convert_from_path
            import pytesseract
            return '\n'.join(pytesseract.image_to_string(im) for im in convert_from_path(str(p), dpi=220)), 'pdf_ocr'
        except Exception: return '', 'pdf_no_text_or_ocr_unavailable'
    if ext in {'.png', '.jpg', '.jpeg'}:
        try:
            from PIL import Image
            import pytesseract
            return pytesseract.image_to_string(Image.open(p)), 'image_ocr'
        except Exception: return '', 'ocr_unavailable'
    return '', 'unsupported'

def extract_fields(text: str):
    clean = re.sub(r'[ \t]+', ' ', text or '')
    patterns = {
      'student_name': [r'(?:student\s*name|name\s*of\s*(?:the\s*)?student|awarded\s*to)\s*[:\-]?\s*([A-Za-z][A-Za-z .\'-]{2,70})'],
      'university': [r'(?:university|institution|college)\s*[:\-]?\s*([A-Za-z][A-Za-z &.\'-]{2,100})', r'((?:[A-Z][A-Za-z&.\'-]*\s+){1,6}(?:University|Institute|College))'],
      'degree': [r'(?:degree|qualification|program(?:me)?)\s*[:\-]?\s*((?:Bachelor|Master|Doctor|B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|BCA|MCA)[A-Za-z .()&-]{0,65})', r'\b(Bachelor of [A-Za-z &]+|Master of [A-Za-z &]+|B\.?Tech|M\.?Tech|BCA|MCA|B\.?Sc|M\.?Sc)\b'],
      'graduation_year': [r'(?:year\s*of\s*(?:passing|graduation)|graduation\s*year|conferred\s*in)\s*[:\-]?\s*((?:19|20)\d{2})'],
      'credential_id': [r'(?:certificate|credential|registration|serial)\s*(?:id|no\.?|number)?\s*[:#\-]?\s*([A-Z0-9][A-Z0-9\-/]{3,30})']}
    out = {}
    for field, pats in patterns.items():
        out[field] = None
        for pat in pats:
            m = re.search(pat, clean, re.I)
            if m:
                out[field] = re.sub(r'\s+', ' ', m.group(1)).strip(' .,:;\n'); break
    out['extraction_note'] = 'Rule-based extraction; manually review OCR output.'
    return out
