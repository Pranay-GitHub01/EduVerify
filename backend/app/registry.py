import hashlib, json
from .database import connect
from .extractor import read_document, extract_fields

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()

def issue(cid, path, filename, metadata):
    digest = sha256_file(path); text, method = read_document(path); extracted = extract_fields(text)
    fields = {k: metadata.get(k) or extracted.get(k) or '' for k in ('student_name','university','degree','graduation_year')}
    with connect() as con:
        con.execute('''INSERT INTO credentials (credential_id,student_name,university,degree,graduation_year,certificate_hash,original_filename,extracted_text,extraction_json)
          VALUES (?,?,?,?,?,?,?,?,?)''', (cid, fields['student_name'],fields['university'],fields['degree'],str(fields['graduation_year']),digest,filename,text,json.dumps({'fields':extracted,'method':method})))
    return {'credential_id':cid,**fields,'certificate_hash':digest,'status':'ACTIVE','extraction_method':method}

def verify(cid, path):
    digest=sha256_file(path); text,method=read_document(path); extracted=extract_fields(text)
    with connect() as con:
        row=con.execute('SELECT * FROM credentials WHERE credential_id=?',(cid,)).fetchone() if cid else con.execute('SELECT * FROM credentials WHERE certificate_hash=?',(digest,)).fetchone()
        reasons=[]; checks={}; record=None
        if not row: result='NOT_FOUND'; reasons.append('No issuer-registered record was found.')
        elif row['status']=='REVOKED': result='REVOKED'; reasons.append('The issuer has revoked this credential.')
        elif row['certificate_hash']!=digest: result='TAMPERED'; reasons.append('Credential ID exists, but SHA-256 differs from the registered original.')
        else: result='VERIFIED'; reasons.append('Exact SHA-256 match with an active issuer-registered record.')
        if row:
            for key in ('student_name','university','degree','graduation_year'):
                observed=extracted.get(key); expected=row[key]
                if observed and expected: checks[key]={'uploaded':observed,'registered':expected,'match':observed.casefold() in expected.casefold() or expected.casefold() in observed.casefold()}
            record=dict(row); record.pop('extracted_text',None); record.pop('extraction_json',None)
        con.execute('INSERT INTO verification_logs (credential_id,uploaded_hash,result,details) VALUES (?,?,?,?)',(cid,digest,result,json.dumps(reasons)))
    return {'result':result,'credential_id':cid,'uploaded_hash':digest,'hash_match':bool(row and row['certificate_hash']==digest),'registry_record':record,'metadata_checks':checks,'extracted_fields':extracted,'extraction_method':method,'reasons':reasons}

def list_credentials():
    with connect() as con:
        return [dict(r) for r in con.execute('SELECT id,credential_id,student_name,university,degree,graduation_year,certificate_hash,status,issued_at,revoked_at FROM credentials ORDER BY id DESC').fetchall()]

def revoke(cid):
    with connect() as con: return con.execute("UPDATE credentials SET status='REVOKED',revoked_at=CURRENT_TIMESTAMP WHERE credential_id=? AND status='ACTIVE'",(cid,)).rowcount>0

def dashboard():
    with connect() as con:
        count=lambda q: con.execute(q).fetchone()[0]
        recent=con.execute('SELECT credential_id,result,checked_at FROM verification_logs ORDER BY id DESC LIMIT 8').fetchall()
        return {'total_credentials':count('SELECT COUNT(*) FROM credentials'),'active_credentials':count("SELECT COUNT(*) FROM credentials WHERE status='ACTIVE'"),'revoked_credentials':count("SELECT COUNT(*) FROM credentials WHERE status='REVOKED'"),'verification_checks':count('SELECT COUNT(*) FROM verification_logs'),'recent_verifications':[dict(x) for x in recent]}
