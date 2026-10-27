import tempfile, unittest
from app.extractor import extract_fields
from app.registry import sha256_file
class CoreTests(unittest.TestCase):
 def test_extract(self):
  d=extract_fields('Student Name: Aditi Sharma\nUniversity: North Valley University\nGraduation Year: 2024\nCertificate ID: EV-DEMO-001')
  self.assertEqual(d['student_name'],'Aditi Sharma'); self.assertEqual(d['graduation_year'],'2024')
 def test_hash(self):
  with tempfile.NamedTemporaryFile(delete=False) as f: f.write(b'original'); p=f.name
  h=sha256_file(p); self.assertEqual(h,sha256_file(p))
  with open(p,'wb') as f: f.write(b'changed')
  self.assertNotEqual(h,sha256_file(p))
if __name__=='__main__': unittest.main()
