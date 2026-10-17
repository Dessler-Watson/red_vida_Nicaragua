"""Receptor de desarrollo RedVida: archivos estáticos + recepción real idempotente.
No es infraestructura oficial de SINAPRED. Mantener en loopback para desarrollo.
Despliegue público requiere HTTPS, autenticación, autorización y política de datos.
"""
import argparse, base64, hashlib, json, re, sqlite3, uuid
from datetime import datetime, timezone
from contextlib import closing
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
MAX_BODY = 10 * 1024 * 1024
TYPES = {'Inundación','Terremoto','Deslizamiento','Tormenta o huracán','Otro fenómeno natural'}
NEEDS = {'Atención médica','Agua','Alimentos','Refugio','Evacuación','Otras'}
FIELDS = {'id','createdAt','disasterType','location','latitude','longitude','coordinateSource','description','affectedPeople','injured','trapped','needs','damage','photo','accuracy','source','demoOrigin','status','priority','verificationStatus','locationVerification','assignmentStatus','followUp'}

def prepare_database(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as db:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('CREATE TABLE IF NOT EXISTS reports (report_id TEXT PRIMARY KEY, payload TEXT NOT NULL, digest TEXT NOT NULL, receipt_id TEXT UNIQUE NOT NULL, received_at TEXT NOT NULL)')
        db.commit()

def validated_report(value):
    if not isinstance(value, dict): raise ValueError('Reporte inválido')
    r = {k:v for k,v in value.items() if k in FIELDS}
    if not isinstance(r.get('id'),str) or not re.fullmatch(r'RVN-[A-Z0-9-]{1,100}',r['id']): raise ValueError('ID inválido')
    if r.get('disasterType') not in TYPES: raise ValueError('Tipo inválido')
    location=r.get('location')
    if not isinstance(location,dict): raise ValueError('Ubicación inválida')
    for key,limit in [('department',100),('municipality',100),('community',180)]:
        if not isinstance(location.get(key),str) or not location[key].strip() or len(location[key])>limit: raise ValueError('Ubicación incompleta')
    if not isinstance(r.get('description'),str) or not 10<=len(r['description'].strip())<=1500: raise ValueError('Descripción inválida')
    for key in ('affectedPeople','injured','trapped'):
        if type(r.get(key)) is not int or not 0<=r[key]<=10000000: raise ValueError('Cantidad inválida')
    lat,lon=r.get('latitude'),r.get('longitude')
    if (lat is None)!=(lon is None): raise ValueError('Coordenadas incompletas')
    if lat is not None and (type(lat) not in (int,float) or type(lon) not in (int,float) or not -90<=lat<=90 or not -180<=lon<=180): raise ValueError('Coordenadas inválidas')
    if not isinstance(r.get('needs'),list) or any(n not in NEEDS for n in r['needs']): raise ValueError('Necesidades inválidas')
    if r.get('source') not in ('citizen','demo'): raise ValueError('Fuente inválida')
    try: datetime.fromisoformat(r['createdAt'].replace('Z','+00:00'))
    except (KeyError,ValueError,TypeError,AttributeError): raise ValueError('Fecha inválida')
    photo=r.get('photo')
    if photo:
        if not isinstance(photo,str) or len(photo)>8000000 or not re.fullmatch(r'data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+',photo): raise ValueError('Fotografía inválida')
        try: base64.b64decode(photo.split(',',1)[1],validate=True)
        except (ValueError,TypeError): raise ValueError('Fotografía inválida')
    r['status']='pending' # El estado remoto se acredita exclusivamente con el recibo.
    return r

class RedVidaHandler(SimpleHTTPRequestHandler):
    def __init__(self,*args,database,**kwargs):
        self.database=database
        super().__init__(*args,directory=str(ROOT),**kwargs)
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        super().end_headers()
    def reply(self,status,body):
        data=json.dumps(body,ensure_ascii=False,allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.end_headers()
        self.wfile.write(data)
    def receipt(self,row):
        return {'reportId':row[0],'receiptId':row[3],'receivedAt':row[4],'status':'received','receiver':'redvida-local'}
    def do_GET(self):
        route=urlsplit(self.path).path
        if route=='/api/health': return self.reply(200,{'server':'redvida-local','status':'ready'})
        if route=='/api/reports':
            with closing(sqlite3.connect(self.database,timeout=20)) as db:
                rows=db.execute('SELECT * FROM reports ORDER BY received_at DESC').fetchall()
            return self.reply(200,{'server':'redvida-local','reports':[{'report':json.loads(r[1]),'receipt':self.receipt(r)} for r in rows]})
        # No exponer la base de datos, código del receptor, archivos de pruebas o listados.
        target=Path(self.translate_path(route)).resolve()
        if not target.is_relative_to(ROOT) or (target.relative_to(ROOT).parts[:1]==('data',) or (target.relative_to(ROOT).parts[:1]==('tests',) and not getattr(self.server,'allow_tests',False))) or (target.is_file() and target.suffix not in {'.html','.css','.js','.svg','.png','.jpg','.avif','.webp','.ico','.webmanifest','.txt'}):
            return self.reply(404,{'error':'Recurso no disponible'})
        super().do_GET()
    def list_directory(self,path):
        self.send_error(404,'No se permiten listados de directorio')
    def do_POST(self):
        if urlsplit(self.path).path!='/api/reports': return self.reply(404,{'error':'Ruta no disponible'})
        origin=self.headers.get('Origin')
        if origin and urlsplit(origin).netloc!=self.headers.get('Host'): return self.reply(403,{'error':'Origen no permitido'})
        if self.headers.get_content_type()!='application/json': return self.reply(415,{'error':'Se requiere JSON'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=MAX_BODY: return self.reply(413,{'error':'Tamaño inválido'})
            payload=json.loads(self.rfile.read(size),parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Número no finito')))
            if payload.get('schemaVersion')!=1: raise ValueError('Versión incompatible')
            report=validated_report(payload.get('report'))
            if self.headers.get('Idempotency-Key')!=report['id']: raise ValueError('Clave de idempotencia inválida')
            canonical=json.dumps(report,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
            digest=hashlib.sha256(canonical.encode()).hexdigest()
            with closing(sqlite3.connect(self.database,timeout=20)) as db:
                db.execute('BEGIN IMMEDIATE')
                existing=db.execute('SELECT * FROM reports WHERE report_id=?',(report['id'],)).fetchone()
                if existing:
                    if existing[2]!=digest: return self.reply(409,{'error':'El ID ya existe con otro contenido; se conserva el original'})
                    return self.reply(200,self.receipt(existing))
                received=datetime.now(timezone.utc).isoformat()
                receipt_id='ACK-'+str(uuid.uuid4())
                db.execute('INSERT INTO reports VALUES (?,?,?,?,?)',(report['id'],canonical,digest,receipt_id,received))
                db.commit() # Confirmar el guardado antes de entregar el acuse.
                row=(report['id'],canonical,digest,receipt_id,received)
            return self.reply(201,self.receipt(row))
        except (ValueError,TypeError,AttributeError,UnicodeError) as error: return self.reply(400,{'error':str(error)})
        except sqlite3.Error: return self.reply(503,{'error':'Almacenamiento temporalmente no disponible; reintenta con el mismo ID'})

def make_server(host,port,database,allow_tests=False):
    prepare_database(database)
    server=ThreadingHTTPServer((host,port),partial(RedVidaHandler,database=str(database)))
    server.allow_tests=allow_tests
    return server

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8080)
    parser.add_argument('--allow-tests',action='store_true',help='Solo laboratorio en loopback')
    parser.add_argument('--data',type=Path,default=ROOT/'data'/'redvida.sqlite3')
    args=parser.parse_args()
    print(f'RedVida local: http://localhost:{args.port} · receptor real de desarrollo, no SINAPRED',flush=True)
    try: make_server(args.host,args.port,args.data,args.allow_tests and args.host in ('127.0.0.1','localhost')).serve_forever()
    except KeyboardInterrupt: pass
