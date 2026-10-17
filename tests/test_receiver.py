"""Pruebas sin datos personales. Ejecutar: python tests/test_receiver.py"""
import importlib.util,json,tempfile,threading,unittest,urllib.request,urllib.error,concurrent.futures
from pathlib import Path
spec=importlib.util.spec_from_file_location('receiver',Path(__file__).resolve().parents[1]/'servidor.py')
receiver=importlib.util.module_from_spec(spec);spec.loader.exec_module(receiver)
class ReceiverTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.server=receiver.make_server('127.0.0.1',0,Path(cls.tmp.name)/'reports.sqlite3');cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.url=f'http://127.0.0.1:{cls.server.server_port}'
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.tmp.cleanup()
 def report(self,id):return {'id':id,'createdAt':'2026-10-16T12:00:00Z','disasterType':'Inundación','location':{'department':'Managua','municipality':'Managua','community':'FICTICIO · prueba'},'latitude':None,'longitude':None,'description':'Datos ficticios para validar el receptor de desarrollo.','affectedPeople':8,'injured':0,'trapped':0,'needs':['Agua'],'source':'demo','demoOrigin':'user-test'}
 def post(self,r,**headers):
  req=urllib.request.Request(self.url+'/api/reports',json.dumps({'schemaVersion':1,'report':r}).encode(),{'Content-Type':'application/json','Idempotency-Key':r['id'],**headers},method='POST')
  try:
   with urllib.request.urlopen(req) as response:return response.status,json.load(response)
  except urllib.error.HTTPError as error:return error.code,json.load(error)
 def test_a_receive_and_repeat(self):
  r=self.report('RVN-TEST-ACK');first=self.post(r);second=self.post(r);self.assertEqual(first[0],201);self.assertEqual(second[0],200);self.assertEqual(first[1],second[1])
 def test_b_conflict_preserves_original(self):
  r=self.report('RVN-TEST-CONFLICT');self.post(r);r['description']='Otro texto ficticio incompatible con el mismo ID.';self.assertEqual(self.post(r)[0],409)
 def test_c_concurrent_retries_one_copy(self):
  r=self.report('RVN-TEST-CONCURRENT')
  with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(lambda _:self.post(r),range(6)))
  self.assertEqual(sum(status==201 for status,_ in results),1);self.assertEqual(len({body['receiptId'] for _,body in results}),1)
  data=json.load(urllib.request.urlopen(self.url+'/api/reports'));self.assertEqual(sum(e['report']['id']==r['id'] for e in data['reports']),1)
 def test_d_reject_invalid_and_cross_origin(self):
  r=self.report('RVN-TEST-INVALID');r['injured']=-1;self.assertEqual(self.post(r)[0],400);r['injured']=0;self.assertEqual(self.post(r,Origin='https://otro.example')[0],403)
 def test_e_receipt_survives_database_reopen(self):
  r=self.report('RVN-TEST-PERSIST');receipt=self.post(r)[1];receiver.prepare_database(Path(self.tmp.name)/'reports.sqlite3');self.assertEqual(self.post(r)[1],receipt)
 def test_f_no_private_files(self):
  for path in ['/servidor.py','/%64ata/redvida.sqlite3','/assets/../data/redvida.sqlite3']:
   with self.assertRaises(urllib.error.HTTPError) as context:urllib.request.urlopen(self.url+path)
   self.assertEqual(context.exception.code,404)
if __name__=='__main__':unittest.main()
