importScripts('js/sync-config.js','js/storage.js','js/sync.js');
const CACHE='redvida-v14-mobile-sync';
const FILES=['css/movil.css','js/sync-config.js','js/sync.js','assets/icon-192.png','assets/icon-512.png','./','index.html','sinapred.html','css/styles.css','css/sinapred.css','js/storage.js','js/ciudadano.js','js/sinapred.js','js/pwa.js','js/map-config.js','assets/logo.svg','assets/vendor/leaflet.js','assets/vendor/leaflet.css','manifest.webmanifest','assets/vendor/images/layers.png','assets/vendor/images/layers-2x.png','assets/vendor/images/marker-icon.png','assets/vendor/images/marker-icon-2x.png','assets/vendor/images/marker-shadow.png'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('redvida-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
// La navegación usa red cuando existe; todos los esenciales tienen respaldo local.
// Las teselas externas no se guardan ni se anuncian como cartografía offline.
self.addEventListener('fetch',e=>{const url=new URL(e.request.url);if(e.request.method!=='GET'||url.origin!==location.origin||url.pathname.startsWith('/api/'))return;
 if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).then(async response=>{if(response.ok&&FILES.some(f=>new URL(f,self.registration.scope).pathname===url.pathname)){const cache=await caches.open(CACHE);await cache.put(e.request,response.clone())}return response}).catch(async()=>await caches.match(e.request)||await caches.match(new URL(url.pathname.endsWith('sinapred.html')?'sinapred.html':'index.html',self.registration.scope).href)));return}
 e.respondWith(caches.match(e.request).then(cached=>cached||fetch(e.request)));
});

self.addEventListener('sync',e=>{if(e.tag==='redvida-outbox')e.waitUntil((async()=>{await RedVidaSync.flush();const queue=await RedVidaStorage.getOutbox();if(queue.some(i=>i.state!=='blocked'))throw Error('Quedan reportes pendientes; reintentar cuando el navegador lo permita.')})())});
