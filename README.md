# RedVida Nicaragua — app móvil offline y receptor de reportes

El informe general del proyecto, el reto 09, las funciones implementadas, las pruebas y los límites de esta entrega está en [INFORME_PROYECTO_REDVIDA.md](INFORME_PROYECTO_REDVIDA.md).

## Entorno elegido

La app ciudadana es una **PWA instalable**, creada con HTML, CSS y JavaScript puro. Se conserva el proyecto de `C:\Users\User\Desktop\RedVida Nicaragua`, su formulario y el panel administrativo. No se ha generado un APK ni se requiere Android Studio para esta etapa.

- Interfaz móvil: `index.html`, `css/movil.css`, `js/ciudadano.js`.
- Trabajo sin internet: IndexedDB y Service Worker.
- Envío: cola persistente `outbox`, `js/sync.js` y `js/sync-config.js`.
- Receptor real de desarrollo: `servidor.py`, Python estándar y SQLite.
- Administrador: `sinapred.html`, con lectura del receptor además de los registros locales.

La recepción por **RedVida** es real cuando hay un recibo del receptor. No equivale a una recepción institucional por SINAPRED. Los recursos, refugios y asignaciones operativas siguen siendo demostrativos.

## Iniciar la aplicación

Desde la carpeta del proyecto, en PowerShell:

    .\iniciar.ps1

O, con Python instalado:

    python servidor.py --port 8080

El script iniciar.ps1 usa el Python disponible en este equipo. El servidor debe permanecer abierto para recibir datos; la app ya cargada puede seguir guardando sin él.

Abrir:

- App ciudadana: http://localhost:8080/index.html
- Administrador: http://localhost:8080/sinapred.html
- Estado del receptor: http://localhost:8080/api/health

**Ya no basta `python -m http.server` para enviar reportes.** Ese comando solo entrega archivos y no implementa la API receptora. Usa servidor.py o iniciar.ps1.

El servidor se limita a `127.0.0.1` de forma predeterminada. No se publica en internet ni se expone automáticamente a la red local. Los datos recibidos se guardan en `data/redvida.sqlite3`, con archivos auxiliares de SQLite cuando corresponda. No borres esa carpeta si deseas conservarlos.

## Instalar y probar en un teléfono real

La PWA requiere una primera carga y preparación de caché. En Android puede instalarse desde un navegador compatible; el botón Instalar usa el aviso del navegador cuando está disponible. En iPhone se ofrecen instrucciones para Compartir → Añadir a pantalla de inicio.

Para que un teléfono acceda fuera de esta computadora necesitamos **publicar la app y el receptor bajo una dirección HTTPS accesible**, con un certificado válido. `localhost` en el teléfono apunta al propio teléfono, no a esta computadora. Abrir una IP de la computadora por HTTP no sustituye los requisitos de seguridad de instalación y Service Worker.

Esta entrega está comprobada en localhost y con vistas móviles del navegador; no es todavía un despliegue público ni una prueba física en Android/iPhone. El siguiente paso de distribución es elegir el dominio/alojamiento HTTPS y preparar el acceso del administrador.

Para esta etapa mantenemos la PWA porque reutiliza toda la interfaz actual. Si después se exige un APK y trabajo nativo específico en segundo plano, se puede planificar una adaptación móvil con Capacitor/Android Studio; no se ha implementado esa adaptación.

## Diseño ciudadano

Inicio editorial en verde profundo, símbolo vectorial propio de pulso, corazón y protección, señales animadas y botón coral. Selección fotográfica por desastre, cuatro pasos, confirmación con acuse real, historial con búsqueda y consejos desplegables. Fuentes Manrope/Inter, Lucide y fotos WebP se cargan desde archivos locales. Se respeta `prefers-reduced-motion`. Las fotografías son de referencia; no representan reportes ni sucesos actuales en Nicaragua. Créditos y licencias en `assets/CREDITS.md`.

## Flujo de guardado y envío

1. La persona completa los cuatro pasos y las necesidades, con GPS opcional o ubicación manual.
2. Se genera un ID estable con UUID completo. El reporte y su trabajo de envío se guardan **en la misma transacción IndexedDB**.
3. Si no hay conexión, queda pendiente. La app no necesita red para conservar texto, coordenadas ya obtenidas y fotografía local.
4. Al volver la conectividad, abrir/reanudar la app o durante los reintentos programados con la app activa, se envía el trabajo pendiente.
5. El cuerpo y la clave `Idempotency-Key` se conservan entre intentos. El servidor usa la clave primaria del reporte y comprueba el contenido; un reintento idéntico devuelve el mismo recibo. Un mismo ID con otro contenido devuelve conflicto 409 y conserva el original.
6. Solo un acuse válido con el ID correspondiente cambia el estado a **Recibido por servidor RedVida**. Un corte después del guardado remoto y antes de recibir la respuesta conserva el trabajo local para recuperar ese mismo recibo.
7. El administrador consulta el receptor al abrirse y periódicamente mientras está visible. Importa los recibos sin duplicar registros y conserva sus cambios operativos locales.

Se usa una reserva transaccional temporal de trabajos para evitar que dos pestañas o un Service Worker envíen simultáneamente el mismo trabajo. Los errores de red y tiempos de espera se reintentan con espera creciente. Los errores que requieren intervención, como un conflicto de contenido, conservan el reporte y muestran que debe revisarse; el botón Enviar permite un intento manual.

El envío con la **app cerrada** depende de Background Sync y de las políticas del navegador/sistema. No se promete ejecución permanente ni inmediata en todos los iPhone o Android. La garantía implementada es guardar primero y reintentar al recuperar conectividad con la app abierta/reanudada; se solicita sincronización en segundo plano cuando existe soporte.

## Datos de prueba y estados honestos

Los ejemplos precargados y las pruebas del usuario **no se transmiten automáticamente**. En el detalle de una prueba pendiente existe Enviar prueba al receptor RedVida y una confirmación explícita. Así puedes demostrar el envío sin hacer pasar datos ficticios por reportes ciudadanos reales.

Las etiquetas separan:

- REPORTE CIUDADANO: datos introducidos sin marcar prueba, pendientes de verificación.
- PRUEBA DEL USUARIO: formulario marcado como ficticio.
- EJEMPLO PRECARGADO: escenario de demostración con coordenadas ilustrativas.

Los estados son: pendiente de envío, intentando enviar, pendiente que requiere revisión, recibido por servidor RedVida, o recepción simulada. La simulación antigua sigue disponible para pruebas que no tengan recepción real; no sobrescribe un recibo real. Los registros recibidos no se eliminan desde el botón de borrado local: existe una copia en el receptor y la eliminación remota todavía no se ha implementado.

## Demostración recomendada

1. Ejecuta iniciar.ps1 y abre ciudadanía y administrador. Espera el aviso de preparación offline.
2. Crea un reporte ficticio, marca la casilla de prueba y guárdalo. Comprueba ID, necesidades y persistencia al recargar.
3. Abre el detalle y confirma Enviar prueba al receptor RedVida. Debe aparecer **Recibido por servidor RedVida · prueba**.
4. Para demostrar que el enlace ya no depende únicamente de compartir IndexedDB, abre http://127.0.0.1:8080/sinapred.html. Ese origen tiene otro almacenamiento del navegador, pero lee el mismo receptor. Debe importar el ID recibido desde localhost.
5. Busca y filtra el reporte, revisa su prioridad y registra una asignación ficticia. La revisión, el inventario y las asignaciones siguen guardándose en el navegador del operador. Su sincronización entre varios operadores o de vuelta al teléfono es una fase pendiente, no una función que se afirme como terminada.
6. Los reportes que tienen coordenadas válidas aparecen en el mapa. Los manuales sin coordenadas permanecen en la tabla. No se inventan puntos para completarlos.

Para una prueba automática sin tocar los datos de demostración del puerto 8080, usa el laboratorio descrito abajo. Sus fixtures usan datos expresamente ficticios aunque ejerciten la ruta de envío de `source=citizen`.

## Probar offline y reconexión

1. Con el servidor activo, carga ambas páginas y espera **Aplicación preparada para abrir sin conexión**.
2. En herramientas del navegador, Application / Service Workers debe mostrar el registro activo de sw.js. No actives Bypass for network para esta prueba.
3. Selecciona Offline en Network o desconecta la conexión del dispositivo. Recarga y crea un reporte. El ID y los datos deben persistir. Para ensayar con datos ficticios, usa el laboratorio o confirma explícitamente el envío de una prueba; no marques un desastre ficticio como reporte real en la demostración principal.
4. Vuelve a Online con el receptor accesible y mantén/reanuda la app. El trabajo pendiente se envía y solo un recibo real cambia su estado.
5. La prueba equivalente del laboratorio detiene el receptor, crea un fixture y vuelve a iniciarlo. Se comprobó la transición de pendiente a recibido sin pulsar Enviar. Esa prueba corta el acceso al receptor, no necesariamente la conectividad general del equipo.

Las teselas cartográficas de OpenStreetMap requieren internet. Las pantallas, las capas locales, los formularios y la cola no dependen de ellas. No se promete mapa base completo offline. INETER y densidad poblacional no están integrados ni se anuncian como capas oficiales verificadas.

## Pruebas

Se comprobaron **27 pruebas automatizadas**:

- 15 de regresión de IndexedDB: validaciones, IDs, fuentes, deduplicación local, revisión, asignaciones concurrentes, inventario, historial y caché.
- 6 del receptor: acuse estable, conflicto de contenido, solicitudes simultáneas con una sola copia, entradas inválidas/origen, persistencia SQLite y protección de archivos privados.
- 6 de envío desde navegador: cola atómica, pérdida de la respuesta después del guardado real, recuperación del mismo recibo, exclusión de ejemplos, importación sin duplicados y envío automático sin pulsar Enviar.

Adicionalmente se probó la reconexión real tras detener/reiniciar el receptor del laboratorio y se consultó una recepción en un administrador con almacenamiento independiente. Ninguna prueba utiliza información personal ni el GPS físico del usuario.

Pruebas del receptor, sin dependencias adicionales:

    python tests/test_receiver.py

Laboratorio separado, desde la carpeta del proyecto:

    python servidor.py --port 8081 --data data/laboratorio.sqlite3 --allow-tests

En ese origen aislado abrir:

- http://localhost:8081/tests/audit.html
- http://localhost:8081/tests/sync-test.html

El ejecutor de envío tiene un botón Crear fixture para reconexión automática. Con la página ya cargada, detén el receptor del puerto 8081, pulsa ese botón, verifica pendiente y vuelve a iniciar el mismo comando. Debe recibirse por los reintentos automáticos sin otro clic. Los datos del puerto 8081 y su SQLite de laboratorio están separados de la demostración principal.

## Almacenamiento y archivos clave

IndexedDB `redvida-nicaragua`, versión **3**, conserva `reports` y `operations` y añade `outbox`. El esquema anterior se conserva; los reportes existentes no se borran. Los nuevos reportes ciudadanos se encolan atómicamente. Al iniciar, los ciudadanos pendientes anteriores también se preparan para envío. Cada trabajo conserva payload, intentos, fecha de reintento, reserva temporal y último error. Los recibos se conservan en el reporte tras retirar el trabajo de la cola.

`operations` conserva inventario y decisiones locales del operador. `data/redvida.sqlite3` conserva las copias recibidas centralmente por este receptor. No borres datos del navegador ni la base del receptor para actualizar la aplicación. Si una pestaña antigua bloquea la actualización de IndexedDB, ciérrala y recarga.

API compartida nueva: enqueueReport, getOutbox, claimNext, finishAttempt, importServerReports, validReceipt y transmissionLabel. Se mantienen los métodos originales de reportes, inventario e historial.

## Contrato del receptor

`js/sync-config.js` usa `/api/reports` en el mismo origen.

POST /api/reports:

    Content-Type: application/json
    Idempotency-Key: <ID estable del reporte>
    {"schemaVersion":1,"report":{...reporte...}}

Respuesta, únicamente después de confirmar el guardado:

    {"reportId":"RVN-...","receiptId":"ACK-...","receivedAt":"fecha ISO","status":"received","receiver":"redvida-local"}

GET /api/reports devuelve objetos `{report, receipt}` para el panel. La API no se cachea en el Service Worker. El endpoint y su contrato deben adaptarse expresamente si se conecta otra plataforma. No se deduce una API a partir de una URL visual ni se afirma integración institucional.

## Alcance para una publicación real

El receptor actual es de desarrollo y funciona por defecto únicamente en esta computadora. Antes de exponerlo públicamente se necesita HTTPS, autenticación y autorización del panel, controles de acceso, copias de seguridad y definición del tratamiento de datos. No se han añadido credenciales ficticias ni se ha publicado automáticamente el servidor.

| Operativo ahora | Pendiente o dependiente |
|---|---|
| PWA y diseño móvil; formulario offline; cola persistente; reintentos; recepción real local; deduplicación y recibos; consulta desde el panel | Dirección HTTPS para teléfonos reales, autenticación, integración oficial SINAPRED y distribución pública |
| Inventario y asignaciones de demostración guardados localmente | Sincronización de decisiones operativas entre varios operadores y hacia el teléfono |
| Solicitud de Background Sync cuando existe soporte | Garantía universal de envío con app cerrada; requeriría evaluar capacidades nativas y del sistema |
| Leaflet incluido localmente y marcadores con datos válidos | Teselas OpenStreetMap online; INETER sin integrar; no hay capa oficial de densidad |



## Rediseño ciudadano premium (16 de octubre de 2026)

El formulario ahora tiene cuatro pasos: categoría fotográfica, GPS/referencia manual, situación y revisión. Nombre completo es el único dato personal solicitado; la descripción, cantidades, necesidades y fotografía son opcionales. Con GPS, los campos territoriales son opcionales; sin GPS es necesaria una referencia. Departamento y municipio no informados quedan «Por determinar», sin geocodificación inventada. Las cantidades desconocidas conservan `countsUnknown`; no se interpretan como ausencia de afectados.

Cambios principales: `index.html`, `js/ciudadano.js`, `js/pwa.js`, `css/ciudadano-premium.css`, `sw.js`, `manifest.webmanifest`, `css/identidad.css`, `servidor.py` (formatos estáticos WebP/WOFF2 y MIME), `tests/audit.js`, `tests/test_receiver.py`. El esquema de IndexedDB, la cola, el motor `js/sync.js` y los contratos de recepción permanecen iguales a la versión anterior. Las versiones de JS/CSS en las URLs evitan que un Service Worker anterior combine la nueva página con el formulario viejo.

Recursos añadidos: cuatro fotos WebP optimizadas (aprox. 323 KB en total), `otro.svg`, Manrope e Inter WOFF2 y Lucide 0.468.0 local con licencias. La fotografía de tormenta muestra rayos; la de deslizamiento muestra una ladera erosionada. Todas son ilustrativas.

### Validación del rediseño

- 8 pruebas del receptor: recepción, reintento idempotente, conflicto, concurrencia, validación, persistencia, nombre/indicador de datos faltantes, protección de archivos y recursos estáticos.
- 15 pruebas de IndexedDB y caché en laboratorio separado; incluye todos los recursos esenciales del rediseño.
- 6 pruebas de sincronización: pérdida de respuesta después de guardar, mismo acuse sin duplicado, cola atómica, exclusión de demos, importación idempotente y envío automático.
- Flujo visual de cuatro pasos con referencia manual, necesidades, edición hacia atrás, confirmación real, búsqueda y detalles.
- Receptor detenido: guardado, recarga desde caché y navegación con cinco imágenes locales cargadas. Al reiniciarlo, el reporte pendiente se recibe automáticamente sin pulsar Enviar.
- Navegador de escritorio con tamaños móviles/tablet/escritorio; comprobar también en un iPhone físico antes de una presentación pública.

No se ha comprobado aquí instalación real en iOS, permiso y precisión GPS del teléfono, persistencia tras desinstalar/borrar datos, ni envío con la aplicación cerrada. La cartografía OpenStreetMap requiere internet y puede fallar de forma independiente; se puede seguir reportando sin ella.

## RedVida Alerta — simulación colaborativa

Consulta `REDVIDA_ALERTA.md` para la propuesta del reto 09, arquitectura, reglas demostrativas, flujo completo, archivos, pruebas y limitaciones.

En el administrador está «Eventos sísmicos». En la interfaz ciudadana, el bloque «RedVida Alerta» permite activar audio/notificaciones de prueba y consultar eventos. Los nuevos avisos llegan por consulta al receptor cada 4 segundos cuando la página puede ejecutarse y hay conexión. No hay sensores reales ni Web Push configurado; no se garantiza entrega con la aplicación cerrada.

El receptor migra de forma aditiva: crea `demo_events` y `demo_event_actions`, conserva `reports` y añade GET/POST `/api/demo-events`. Requiere reiniciar `servidor.py` tras actualizar el código. Los reportes y la cola existente conservan sus contratos.

Pruebas del módulo: `python -m unittest discover -s tests -p "test_*.py"`; navegador en laboratorio `http://localhost:8081/tests/alerta-test.html`. Para iniciar el laboratorio: `python servidor.py --port 8081 --data RUTA_A_BASE_SEPARADA.sqlite3 --allow-tests`. No reutilizar una base del entorno habitual.


## Corrección: alerta roja al iniciar

Consultar [ALERTA_ROJA.md](ALERTA_ROJA.md) para el diagnóstico, acceso desde iPhone, publicación explícita al iniciar, magnitud ficticia, acuses reales del navegador y límites de notificación. La PWA utiliza el mismo origen del receptor y consulta cada 4 s; no hay Web Push configurado con la app cerrada.

## Iniciar desde VS Code: un solo origen

Abre la carpeta RedVida Nicaragua y pulsa **Ctrl+Shift+B**: la tarea **RedVida: iniciar servidor** inicia o reutiliza Python en 8080 y muestra los dos enlaces. Mantén la terminal abierta cuando esté ejecutando el servidor. F5 permite elegir **RedVida: app ciudadana** o **RedVida: administrador** en Microsoft Edge, con el receptor ya iniciado.

Usa ambas interfaces en `http://localhost:8080/index.html` y `http://localhost:8080/sinapred.html`. Live Server (5500) no ejecuta las rutas Python; ahora las entradas HTML en 5500 redirigen a localhost:8080, conservando ruta y consulta. Recarga con Ctrl+Shift+R una vez si la pestaña seguía mostrando la versión anterior. No se borran ni migran automáticamente datos guardados en el origen 5500 o 127.0.0.1; esos almacenamientos continúan separados. El módulo ahora se llama **Eventos sísmicos**, conservando etiquetas de simulación en datos ficticios.

## Alerta premium e informe compacto

Consulta [ALERTA_PREMIUM.md](ALERTA_PREMIUM.md) para el nuevo diseño, formulario de situación con GPS opcional, cola persistente y vínculo automático después del recibo real. El botón Informar a las autoridades explica que el destinatario actual es el receptor de demostración RedVida. Todos los informes originados en ejercicios siguen siendo pruebas. Se conservan las limitaciones de sonido, segundo plano y Web Push.

## Nueva composición de alerta

La versión 40 reemplaza la alerta oscura por una cabecera roja, datos sobre blanco y protección breve. El botón **Informar daños y pedir ayuda** aparece completo en la primera pantalla de 360 × 800. Consulta [ALERTA_CLARA.md](ALERTA_CLARA.md) para archivos y validación. Se conservan el formulario, la cola offline y las limitaciones de notificación.

## Textos ciudadanos y control desde administración

La versión 42 elimina de los textos de interfaz ciudadana Simulación y datos ficticios. Los ejercicios conservan un distintivo Aviso de prueba y Magnitud de prueba. Se quitó la opción ciudadana para marcar un reporte normal como prueba y el botón de recepción simulada. Crear y ejecutar ejercicios sigue en Eventos sísmicos del administrador. Se conservan las marcas internas source/demo/isSimulation para no mezclar pruebas y reportes ciudadanos, los registros históricos y sus recibos. No se reescriben reportes almacenados.
