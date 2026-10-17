import unittest,tempfile,threading,uuid,json,urllib.request,urllib.error,sqlite3
from pathlib import Path
import sys
from contextlib import closing
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import servidor
from alertas import group_signals
class AlertTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/'test.sqlite3';self.server=servidor.make_server('127.0.0.1',0,self.path);threading.Thread(target=self.server.serve_forever,daemon=True).start();self.url=f'http://127.0.0.1:{self.server.server_port}';self.eid='EVT-'+uuid.uuid4().hex.upper()
 def tearDown(self):self.server.shutdown();self.server.server_close();self.tmp.cleanup()
 def post(self,payload,origin=None):
  headers={'Content-Type':'application/json','Idempotency-Key':payload.get('actionId','')}
  if origin:headers['Origin']=origin
  request=urllib.request.Request(self.url+'/api/demo-events',json.dumps(payload).encode(),headers,method='POST')
  try:
   with urllib.request.urlopen(request) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as r:return r.code,json.load(r)
 def action(self,action,**extra):return {'eventId':self.eid,'actionId':'ACT-'+uuid.uuid4().hex.upper(),'action':action,'demonstration':True,**extra}
 def create(self):
  p=self.action('create',parameters={'deviceCount':5,'threshold':3,'timeWindowSeconds':10,'distanceKm':2},area={'label':'SIMULACION FICTICIA','latitude':12.1,'longitude':-86.2});self.assertEqual(self.post(p)[0],201);return p
 def signals(self):return [{'deviceId':'DEV-'+uuid.uuid4().hex.upper(),'detectedAt':'2026-10-16T20:00:00Z','latitude':12.1+i*.001,'longitude':-86.2,'synthetic':True} for i in range(3)]
 def ready(self):self.create();p=self.action('signals',signals=self.signals());return self.post(p)[1]['event']
 def test_group_requires_distinct_devices_within_space_and_time(self):
  self.create();signals=self.signals();signals[2]['detectedAt']='2026-10-16T20:01:00Z'
  event=self.post(self.action('signals',signals=signals))[1]['event'];self.assertIsNone(event['candidate']);self.assertEqual(event['state'],'signals_received')
  signals=self.signals();signals[1]['latitude']=15;self.assertEqual(len(group_signals(signals,{'distanceKm':2,'timeWindowSeconds':10})),2)
 def test_deduplicate_signals_actions_and_creation(self):
  creation=self.create();self.assertEqual(self.post(creation)[0],200)
  p=self.action('signals',signals=self.signals());first=self.post(p);self.assertEqual(first,self.post(p));self.assertEqual(first[1]['event']['state'],'pending_verification')
  event=self.post(self.action('signals',signals=p['signals']))[1]['event'];self.assertEqual(len(event['signals']),3)
  p['action']='review';self.assertEqual(self.post(p)[0],409)
 def test_operator_review_publish_close_and_history_persist(self):
  self.create();self.assertEqual(self.post(self.action('publish'))[0],409)
  event=self.post(self.action('signals',signals=self.signals()))[1]['event'];self.assertIsNone(event['alert']);self.assertTrue(any(h['state']=='possible_detected' for h in event['history']))
  self.assertEqual(self.post(self.action('review'))[0],200)
  a=self.post(self.action('publish'))[1]['event']['alert'];b=self.post(self.action('publish'))[1]['event']['alert'];self.assertEqual(a,b);self.assertTrue(a['demonstration'])
  event=self.post(self.action('close'))[1]['event'];self.assertEqual(event['state'],'closed');self.assertEqual(self.post(self.action('publish'))[0],409)
  servidor.prepare_database(self.path);data=json.load(urllib.request.urlopen(self.url+'/api/demo-events'));self.assertEqual(data['events'][0]['history'],event['history'])
 def test_validate_synthetic_source_origin_and_parameters(self):
  p=self.action('create',parameters={'deviceCount':-2},area={});self.assertEqual(self.post(p)[0],400)
  p['demonstration']=False;self.assertEqual(self.post(p)[0],400);self.assertEqual(self.post(p,origin='https://other.example')[0],403)
  self.create();s=self.signals();s[0]['synthetic']=False;self.assertEqual(self.post(self.action('signals',signals=s))[0],400)
 def test_link_report_and_edit_priority_without_changing_report(self):
  self.ready();rid='RVN-TEST-LINK-ALERT';self.assertEqual(self.post(self.action('link_report',reportId=rid))[0],409)
  report={'id':rid,'createdAt':'2026-10-16T20:00:00Z','disasterType':'Terremoto','source':'demo','location':{'department':'Managua','municipality':'Managua','community':'FICTICIO'},'description':'FICTICIO. Fixture para probar vinculacion.','latitude':12.1,'longitude':-86.2,'affectedPeople':3,'injured':1,'trapped':0,'needs':['Agua']}
  req=urllib.request.Request(self.url+'/api/reports',json.dumps({'schemaVersion':1,'report':report}).encode(),{'Content-Type':'application/json','Idempotency-Key':rid},method='POST');urllib.request.urlopen(req).close()
  event=self.post(self.action('link_report',reportId=rid))[1]['event'];self.assertEqual(event['reportIds'],[rid])
  event=self.post(self.action('priority',priority='Alta',reason='Heridos en reporte ficticio'))[1]['event'];self.assertEqual(event['operatorPriority']['level'],'Alta')
  with closing(sqlite3.connect(self.path)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM reports').fetchone()[0],1)
 def test_explicit_start_publishes_magnitude_without_claiming_verification(self):
  p=self.action('create',startAlert=True,magnitude=5.8,parameters={'deviceCount':5,'threshold':3,'timeWindowSeconds':10,'distanceKm':2},area={'label':'ZONA FICTICIA','latitude':12.1,'longitude':-86.2})
  event=self.post(p)[1]['event'];self.assertEqual(event['magnitude'],5.8);self.assertEqual(event['source'],'simulation');self.assertEqual(event['eventType'],'earthquake');self.assertTrue(event['isSimulation']);self.assertIsNotNone(event['alert']);self.assertEqual(event['verificationStatus'],'unverified');self.assertIsNone(event['candidate'])
  self.assertEqual(event,self.post(p)[1]['event'])
  ack=self.action('receipt',deviceId='WEB-TEST-BROWSER-001',stage='received');self.assertEqual(self.post(ack)[0],200);self.assertEqual(self.post(ack)[0],200)
  self.post(self.action('receipt',deviceId='WEB-TEST-BROWSER-001',stage='displayed'))
  self.post(self.action('close'))
  event=self.post(self.action('receipt',deviceId='WEB-TEST-BROWSER-001',stage='acknowledged'))[1]['event'];self.assertEqual(len(event['receipts']),1);self.assertEqual(len(event['receipts']['WEB-TEST-BROWSER-001']),3);self.assertEqual(event['status'],'closed')
  self.assertEqual(self.post(self.action('receipt',deviceId='WEB-TEST-BROWSER-002',stage='push_delivered'))[0],400)
if __name__=='__main__':unittest.main()

