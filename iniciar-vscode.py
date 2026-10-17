"""Start or reuse the local RedVida receiver from the VS Code task."""
import json
import runpy
import sys
import urllib.request
from pathlib import Path

ready = False
try:
    with urllib.request.urlopen('http://localhost:8080/api/health', timeout=2) as response:
        health = json.load(response)
        ready = health.get('server') == 'redvida-local' and health.get('status') == 'ready'
except (OSError, ValueError):
    pass

print('App: http://localhost:8080/index.html', flush=True)
print('Administrador: http://localhost:8080/sinapred.html', flush=True)
if ready:
    print('El receptor RedVida ya está iniciado; puedes abrir los enlaces.', flush=True)
else:
    sys.argv = ['servidor.py', '--port', '8080']
    runpy.run_path(str(Path(__file__).with_name('servidor.py')), run_name='__main__')
