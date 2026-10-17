"""Synthetic-event demonstration store. No sensor, seismic or dispatch service."""
import json, math, re, sqlite3, hashlib
from contextlib import closing
from datetime import datetime, timezone

STATES = {'signals_received','pending_verification','confirmed_simulation','closed'}
def now(): return datetime.now(timezone.utc).isoformat()
def encoded(value): return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def moment(value):
    if not isinstance(value,str): raise ValueError('Fecha inválida')
    d=datetime.fromisoformat(value.replace('Z','+00:00'))
    if d.tzinfo is None: raise ValueError('La fecha requiere zona horaria')
    return d.timestamp()
def number(v,lo,hi,integer=False):
    if type(v) not in (int,float) or not math.isfinite(v) or not lo<=v<=hi or (integer and type(v) is not int): raise ValueError('Parámetro demostrativo inválido')
    return v
def label(v,limit=180):
    if not isinstance(v,str) or not v.strip() or len(v)>limit: raise ValueError('Texto inválido')
    return v.strip()
def identifier(v,prefix):
    if not isinstance(v,str) or not re.fullmatch(prefix+r'[A-Z0-9-]{8,100}',v): raise ValueError('Identificador inválido')
    return v
def distance(a,b):
    lat1,lat2=map(math.radians,[a['latitude'],b['latitude']]);dl=math.radians(b['longitude']-a['longitude']);dt=lat2-lat1
    h=math.sin(dt/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(dl/2)**2
    return 6371*2*math.asin(math.sqrt(min(1,h)))
def group_signals(signals,parameters):
    """Demo: anchor radius + rolling time window, distinct synthetic device IDs."""
    best=[]
    for anchor in signals:
        nearby=[s for s in signals if distance(s,anchor)<=parameters['distanceKm']]
        for end in nearby:
            cluster=[s for s in nearby if 0<=moment(end['detectedAt'])-moment(s['detectedAt'])<=parameters['timeWindowSeconds']]
            if len(cluster)>len(best): best=cluster
    return best

def prepare(db):
    db.execute('CREATE TABLE IF NOT EXISTS demo_events (event_id TEXT PRIMARY KEY,payload TEXT NOT NULL,created_at TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS demo_event_actions (action_id TEXT PRIMARY KEY,event_id TEXT NOT NULL,digest TEXT NOT NULL,response TEXT NOT NULL)')

class DemoEvents:
    def __init__(self,path): self.path=path
    def recent(self):
        with closing(sqlite3.connect(self.path,timeout=20)) as db:
            return [json.loads(r[0]) for r in db.execute('SELECT payload FROM demo_events ORDER BY created_at DESC LIMIT 50')]
    def mutate(self,payload,key):
        if not isinstance(payload,dict) or payload.get('demonstration') is not True: raise ValueError('Solo eventos demostrativos')
        eid=identifier(payload.get('eventId'),'EVT-');aid=identifier(payload.get('actionId'),'ACT-')
        if key!=aid: raise ValueError('Clave idempotente inválida')
        digest=hashlib.sha256(encoded(payload).encode()).hexdigest()
        with closing(sqlite3.connect(self.path,timeout=20)) as db:
            db.execute('BEGIN IMMEDIATE')
            done=db.execute('SELECT digest,response FROM demo_event_actions WHERE action_id=?',(aid,)).fetchone()
            if done:
                if done[0]!=digest: return 409,{'error':'La acción ya existe con otro contenido'}
                return 200,json.loads(done[1])
            row=db.execute('SELECT payload FROM demo_events WHERE event_id=?',(eid,)).fetchone()
            action=payload.get('action');at=now()
            if action=='create':
                if row: return 409,{'error':'El evento ya existe; conserva su identificador'}
                p=payload.get('parameters',{});area=payload.get('area',{})
                parameters={'deviceCount':number(p.get('deviceCount'),1,50,True),'threshold':number(p.get('threshold'),2,50,True),'timeWindowSeconds':number(p.get('timeWindowSeconds'),1,120,True),'distanceKm':number(p.get('distanceKm'),.1,50)}
                event={'id':eid,'createdAt':at,'source':'simulation','demonstration':True,'state':'signals_received','verificationStatus':'unverified','parameters':parameters,'area':{'label':label(area.get('label')),'latitude':number(area.get('latitude'),-90,90),'longitude':number(area.get('longitude'),-180,180)},'signals':[],'candidate':None,'alert':None,'reportIds':[],'operatorPriority':None,'history':[]}
                event.update(eventType='earthquake',magnitude=number(payload.get('magnitude',5.8),0,10),locationLabel=event['area']['label'],latitude=event['area']['latitude'],longitude=event['area']['longitude'],isSimulation=True,status='created',receipts={},message='Mantén la calma. Busca protección, aléjate de ventanas y objetos que puedan caer. Protege la cabeza y sigue las indicaciones oficiales de las autoridades.')
                # Explicit operator-started exercise, independent of automatic candidate detection.
                if payload.get('startAlert') is True:
                    event['alert']={'id':'ALT-'+eid[4:],'eventId':eid,'issuedAt':at,'message':event['message'],'demonstration':True,'verificationStatus':'unverified_simulation'}
                    event['status']='published_simulation'
                message='Simulación iniciada. '+('Aviso de ejercicio publicado por acción explícita del operador; candidato sin verificar.' if event['alert'] else 'No hay lectura de sensores reales.')
            else:
                if not row: return 404,{'error':'Evento no encontrado'}
                event=json.loads(row[0])
                if event['state']=='closed' and action!='receipt': return 409,{'error':'El evento está cerrado'}
                if action=='signals':
                    if event['state']=='confirmed_simulation': return 409,{'error':'La simulación ya fue revisada'}
                    supplied=payload.get('signals')
                    if not isinstance(supplied,list) or not 1<=len(supplied)<=50: raise ValueError('Señales inválidas')
                    ids={s['deviceId'] for s in event['signals']}
                    for s in supplied:
                        if not isinstance(s,dict) or s.get('synthetic') is not True: raise ValueError('Solo señales sintéticas')
                        did=identifier(s.get('deviceId'),'DEV-');moment(s.get('detectedAt'))
                        if did in ids: continue
                        if len(event['signals'])>=event['parameters']['deviceCount']: raise ValueError('Más señales que dispositivos configurados')
                        event['signals'].append({'deviceId':did,'detectedAt':s['detectedAt'],'latitude':number(s.get('latitude'),-90,90),'longitude':number(s.get('longitude'),-180,180),'synthetic':True,'state':'received'});ids.add(did)
                    cluster=group_signals(event['signals'],event['parameters'])
                    message='Señales sintéticas recibidas: '+str(len(event['signals']))
                    if len(cluster)>=event['parameters']['threshold'] and not event['candidate']:
                        event['candidate']={'deviceIds':[s['deviceId'] for s in cluster],'detectedAt':at,'rule':'Radio respecto a señal ancla y ventana temporal; regla ficticia, sin validación sísmica'}
                        event['history'].append({'at':at,'state':'possible_detected','message':'Posible evento detectado por la regla demostrativa'})
                        event['state']='pending_verification';message='Pendiente de verificación. Sin alerta autorizada.'
                elif action=='review':
                    if event['state']!='pending_verification': return 409,{'error':'Se requiere un evento candidato pendiente'}
                    event['state']='confirmed_simulation';event['verificationStatus']='reviewed_simulation';message='Confirmado en la simulación por el operador. No es validación científica.'
                elif action=='publish':
                    if event['state']!='confirmed_simulation': return 409,{'error':'Revisa el candidato antes de difundir el simulacro'}
                    if not event['alert']:
                        event['alert']={'id':'ALT-'+eid[4:],'eventId':eid,'issuedAt':at,'area':event['area'],'message':'SIMULACRO: posible movimiento sísmico en el área de referencia. No corresponde a una alerta real.','safety':'Durante un sismo real: agáchate, cúbrete y sujétate; aléjate de ventanas. Sigue las indicaciones de las autoridades.','verificationStatus':'reviewed_simulation','demonstration':True}
                    message='Alerta de prueba disponible para consulta ciudadana. No se acredita recepción institucional.'
                elif action=='receipt':
                    if not event.get('alert'): return 409,{'error':'No existe aviso publicado'}
                    device=identifier(payload.get('deviceId'),'WEB-');stage=payload.get('stage')
                    if stage not in ['received','displayed','acknowledged','notification_requested']: raise ValueError('Acuse inválido')
                    receipts=event.setdefault('receipts',{})
                    if device not in receipts and len(receipts)>=500: raise ValueError('Límite de acuses del ejercicio')
                    receipts.setdefault(device,{}).setdefault(stage,at)
                    message='Acuse declarado por navegador de prueba: '+stage
                elif action=='link_report':
                    rid=identifier(payload.get('reportId'),'RVN-')
                    if not db.execute('SELECT 1 FROM reports WHERE report_id=?',(rid,)).fetchone(): return 409,{'error':'El reporte debe estar recibido por el receptor RedVida antes de asociarlo'}
                    if rid not in event['reportIds']: event['reportIds'].append(rid)
                    message='Reporte asociado explícitamente al simulacro: '+rid
                elif action=='priority':
                    priority=payload.get('priority')
                    if priority not in ['Urgente','Alta','Media','Baja','Por evaluar']: raise ValueError('Prioridad inválida')
                    event['operatorPriority']={'level':priority,'reason':label(payload.get('reason'),500),'updatedAt':at};message='Prioridad del operador: '+priority+' · '+event['operatorPriority']['reason']
                elif action=='close': event['state']='closed';message='Evento cerrado por el operador'
                else: raise ValueError('Acción inválida')
            event['status']='closed' if event['state']=='closed' else ('published_simulation' if event.get('alert') else event['state']);event['updatedAt']=at;event['history'].append({'at':at,'state':event['state'],'message':message})
            if len(event['history'])>300: raise ValueError('Límite de historial del simulacro alcanzado')
            db.execute('INSERT INTO demo_events VALUES (?,?,?) ON CONFLICT(event_id) DO UPDATE SET payload=excluded.payload',(eid,encoded(event),event['createdAt']))
            response={'server':'redvida-local','demonstration':True,'event':event}
            db.execute('INSERT INTO demo_event_actions VALUES (?,?,?,?)',(aid,eid,digest,encoded(response)));db.commit()
            return (201 if action=='create' else 200),response
