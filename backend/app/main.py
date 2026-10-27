from pathlib import Path
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import UPLOAD_DIR, MAX_UPLOAD_MB, ALLOWED_EXTENSIONS, DATA_DIR
from .database import init_db
from . import registry
app=FastAPI(title='EduVerify AI Certificate Verification API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup(): init_db(); UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
async def save_upload(file):
    name=Path(file.filename or 'upload').name; ext=Path(name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS: raise HTTPException(400,'Unsupported file type. Use PDF, PNG, JPG, or TXT.')
    target=UPLOAD_DIR/(uuid.uuid4().hex+ext); size=0
    with target.open('wb') as out:
        while chunk:=await file.read(1024*1024):
            size+=len(chunk)
            if size>MAX_UPLOAD_MB*1024*1024: target.unlink(missing_ok=True); raise HTTPException(413,f'File exceeds {MAX_UPLOAD_MB} MB limit.')
            out.write(chunk)
    return str(target),name
@app.get('/api/health')
def health(): return {'status':'ok','service':'EduVerify API','mode':'AI + local trusted registry'}
@app.get('/api/credentials')
def credentials(): return registry.list_credentials()
@app.get('/api/dashboard')
def stats(): return registry.dashboard()
@app.post('/api/credentials/issue')
async def issue(file:UploadFile=File(...),credential_id:str=Form(...),student_name:str=Form(''),university:str=Form(''),degree:str=Form(''),graduation_year:str=Form('')):
    cid=credential_id.strip()
    if not 4<=len(cid)<=40: raise HTTPException(400,'Credential ID must be 4–40 characters.')
    path,name=await save_upload(file)
    try: return registry.issue(cid,path,name,{'student_name':student_name.strip(),'university':university.strip(),'degree':degree.strip(),'graduation_year':graduation_year.strip()})
    except Exception as exc:
        if 'UNIQUE constraint failed' in str(exc): raise HTTPException(409,'This credential ID is already registered.')
        raise HTTPException(500,f'Could not issue credential: {exc}')
    finally: Path(path).unlink(missing_ok=True)
@app.post('/api/credentials/verify')
async def verify(file:UploadFile=File(...),credential_id:str=Form('')):
    path,_=await save_upload(file)
    try: return registry.verify(credential_id.strip() or None,path)
    finally: Path(path).unlink(missing_ok=True)
@app.post('/api/credentials/{credential_id}/revoke')
def revoke(credential_id:str):
    if not registry.revoke(credential_id): raise HTTPException(404,'Active credential not found.')
    return {'message':'Credential revoked.','credential_id':credential_id,'status':'REVOKED'}
@app.post('/api/demo/seed')
def seed():
    DATA_DIR.mkdir(parents=True,exist_ok=True); p=DATA_DIR/'demo_seed_certificate.txt'
    p.write_text('EDUVERIFY SYNTHETIC DEMONSTRATION CERTIFICATE\nStudent Name: Aditi Sharma\nUniversity: North Valley University\nDegree: Bachelor of Computer Science\nGraduation Year: 2024\nCertificate ID: EV-DEMO-001\nFictional demo data only.\n',encoding='utf-8')
    try:
        if 'EV-DEMO-001' not in {x['credential_id'] for x in registry.list_credentials()}:
            registry.issue('EV-DEMO-001',str(p),p.name,{'student_name':'Aditi Sharma','university':'North Valley University','degree':'Bachelor of Computer Science','graduation_year':'2024'})
        return {'message':'Synthetic demo credential is ready.','credential_id':'EV-DEMO-001'}
    finally: p.unlink(missing_ok=True)
