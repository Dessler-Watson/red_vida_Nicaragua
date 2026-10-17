# RedVida — corrección de entrega y alerta roja

## Diagnóstico comprobado

Antes, Iniciar simulación guardaba un evento sin `alert`. La PWA filtraba eventos que tuvieran `alert` y no estuvieran cerrados. Hacían falta Revisar y confirmar y Simular alerta ciudadana. Por eso iniciar por sí solo no mostraba nada: la interrupción estaba entre la creación del escenario y su publicación, no en SQLite.

Ahora Iniciar simulación envía un POST real a `/api/demo-events`, con `startAlert: true` y magnitud ficticia configurada (5.8 inicialmente). El servidor guarda el ejercicio y el aviso en una transacción SQLite. La PWA consulta ese mismo origen cada 4 segundos y abre la pantalla roja. La publicación expresa de un ejercicio no verifica científicamente el candidato. El simulador sigue generando señales sintéticas y permite revisar el candidato por separado.

No se conoce todavía la dirección exacta que está usando el iPhone; se solicitó al usuario para verificarla. El enlace temporal previo respondió HTTP 302 hacia su acceso protegido al comprobarlo. Esto confirma que exige autenticación, no una entrega al teléfono. No se cambió la dirección del receptor ni el canal de reportes.

## Prueba con el iPhone

1. Mantener encendida la computadora y ejecutando `iniciar.ps1` (servidor Python en 8080).
2. En la computadora abrir `http://localhost:8080/sinapred.html`.
3. En iPhone usar el enlace HTTPS privado vigente que conduce a ese mismo servidor, completar el acceso autorizado y abrir `index.html`. No usar localhost en el teléfono. El túnel temporal puede cambiar o dejar de funcionar.
4. Verificar en RedVida Alerta **Servidor consultado**, **Conectado al receptor** y el contexto seguro. Si aparece un error de sesión, abrir la dirección en Safari y renovar el acceso. Una API inaccesible nunca se presenta como recepción.
5. Para notificaciones en iPhone, añadir la web a inicio desde Safari y abrirla desde su icono. Pulsar **Activar alertas de prueba** o **Activar notificaciones**, conceder permiso si está disponible y usar **Probar sonido**. El audio se habilita por sesión.
6. Mantener la app abierta para esta demostración. En administrador seleccionar Eventos sísmicos, magnitud 5.8 y zona explícitamente ficticia; pulsar **Iniciar simulación** una vez. Debe aparecer la pantalla roja en la siguiente consulta.
7. Consultar instrucciones y reconocer el aviso. Recargar: no debe sonar ni abrirse automáticamente otra vez por el mismo ID. Consultar simulacro permite volver a verlo manualmente.
8. En administrador seleccionar el evento y observar acuses. Cerrar el evento conserva historial. Reiniciar crea otro ID.

Una IP de la computadora mediante HTTP no equivale a un contexto seguro en iPhone; la PWA y notificaciones pueden quedar bloqueadas. No se expuso el servidor por una nueva interfaz de red. Mantener el túnel privado autorizado para HTTPS o configurar un despliegue HTTPS autenticado estable. Ambas interfaces deben utilizar el mismo receptor y base SQLite.

## Estados y acuses honestos

El evento incluye `id`, `eventType: earthquake`, `magnitude`, `locationLabel`, coordenadas ficticias, `createdAt`, `source: simulation`, `isSimulation: true`, `status` y `message`. Conserva los campos previos `state`, `demonstration`, `verificationStatus`, `area`, `signals`, `history`, `reportIds` y prioridad. Los eventos antiguos siguen siendo legibles.

- Publicado: guardado y disponible para consulta, no confirma entrega.
- `received`: el navegador declara haber procesado el aviso.
- `displayed`: el navegador declaró haber abierto el diálogo. No demuestra que una persona lo leyó.
- `acknowledged`: se pulsó reconocer/cerrar (o Escape).
- `notification_requested`: `showNotification()` resolvió. No demuestra lectura, entrega Push o sonido.

Los acuses se guardan por un ID aleatorio de instalación del navegador, sin huella digital ni identificación personal. Dos navegadores del mismo teléfono cuentan por separado; no se anuncian como teléfonos físicos únicos. Se mantienen pendientes localmente si falla el envío y se reintentan mientras la página ejecuta consultas. Los reintentos conservan la clave idempotente. No hay acuses institucionales reales ni contador de Push entregado.

## Aplicación abierta, segundo plano y cerrada

| Escenario | Implementado | Límite |
|---|---|---|
| Abierta y conectada | Consulta real, pantalla roja, magnitud del evento, audio habilitado por gesto y vibración si API admite | El sistema puede bloquear audio/vibración; no supera silencio |
| Segundo plano | Intenta notificación persistente si se recibe el evento y existe permiso; conserva una vista pendiente para el regreso | El navegador puede suspender consultas; no garantiza entrega de eventos nuevos |
| Cerrada | No hay emisor ni suscripción Web Push | Pendiente; no se simula éxito |
| Sin conexión | Interfaz y eventos previamente almacenados disponibles | No recibe eventos remotos nuevos |

Web Push queda pendiente: suscripciones por dispositivo, VAPID, emisor Python, autenticación/roles y pruebas de entrega con app cerrada. No se añadieron claves ficticias ni se anunciaron servicios operativos. [Documentación Apple/WebKit sobre iOS](https://webkit.org/blog/13878/) y [Apple sobre Web Push](https://developer.apple.com/documentation/usernotifications/sending-web-push-notifications-in-web-apps-and-browsers).

## Archivos de esta corrección

- `alertas.py`: esquema compatible, publicación explícita al iniciar, magnitud validada, acuses idempotentes e historial.
- `js/alerta-admin.js`: magnitud configurable, inicio/publicación y contadores de acuses declarados.
- `js/alerta-ciudadano.js`: pantalla roja, activación, señales cortas cancelables, notificaciones, acuses, regreso de segundo plano y deduplicación.
- `js/alerta-core.js`: compatibilidad con ambas fuentes y mensajes de acceso/red.
- `css/alerta.css`: pantalla completa responsive, contraste, animación breve y movimiento reducido.
- `index.html`, `sinapred.html`, `sw.js`: recursos actualizados versión 33. Se conserva apertura del evento desde notificationclick.
- `tests/test_alertas.py`: nueva prueba del inicio/publicación y acuses.
- `tests/alerta-test.js`, `tests/audit.js`: caché actual y espera explícita de actualización del Service Worker.
- `README.md`, `REDVIDA_ALERTA.md` y este documento: procedimiento actualizado.

No se cambian `js/storage.js`, `js/sync.js` ni el contrato o tabla de reportes ciudadanos.

## Validación

Resultados ejecutados: 14 pruebas Python correctas; 8 pruebas de canal/caché en navegador; 15 de IndexedDB/recursos; 6 de cola de envío y receptor. Total 43 comprobaciones correctas. La actualización de caché mostró inicialmente dos fallos de espera entre versiones; se corrigió el arnés para solicitar y esperar explícitamente la actualización y se repitieron las pruebas aisladamente con 8/8 y 15/15.

Flujo manual ejecutado entre administrador localhost:8081 y ciudadano 127.0.0.1:8081 (almacenamientos separados, mismo servidor de laboratorio): Iniciar → POST/SQLite → consulta automática → pantalla roja con magnitud 5.8 y Mantén la calma; emisión del motor de audio y solicitud de vibración; acuses 1 recibido, 1 presentado, 1 reconocido. Tras recargar no reapareció el diálogo y el historial conservó los acuses. El diseño se revisó a 390 × 844 sin desbordamiento horizontal. Consola de ambas interfaces sin errores JavaScript en la revisión. Se guardó captura real de la pantalla roja.

No se ejecutó una notificación real del sistema, ni segundo plano en iOS, ni aplicación cerrada. Web Push está pendiente. No se probó la audibilidad ni vibración física. Los fixtures se ejecutaron en una base de laboratorio distinta y no se publicaron alertas de ensayo en la base principal. La computadora no tiene acceso al iPhone físico del usuario: no se marca como superada ninguna prueba de Safari, pantalla bloqueada, notificación del sistema real, audibilidad o vibración física sin ejecutarla allí.


## Corrección adicional: pestañas antiguas y deduplicación visual

Al revisar las pestañas reales abiertas se encontró una página ciudadana todavía cargada sin `alerta-core.js` ni `alerta-ciudadano.js`; la pestaña original conservaba la versión anterior del formulario. Se actualizó sin borrar IndexedDB. Además, la reclamación global del aviso impedía abrir automáticamente el diálogo en una segunda pestaña del mismo origen. Se separó la presentación visual por pestaña del reclamo compartido para sonido/notificación. Reconocer y recargar una pestaña no la reabre automáticamente, y no cierra el aviso de la otra.

Cambios: `js/alerta-ciudadano.js`; referencias/caché versión 34 en `index.html`, `sinapred.html`, `sw.js`, `tests/alerta-test.js`, `tests/audit.js`; documentación. Se preservan colas y datos.

Prueba manual adicional en el servidor principal 8080: un clic en Iniciar simulación creó EVT-94EEB2AFC51D45F6B3D443431ED9ED8C con magnitud 5.8 en SQLite; ambas pestañas ciudadanas abiertas mostraron automáticamente la pantalla roja del mismo evento. Reconocer/recargar una dejó su diálogo cerrado y el otro continuó abierto. Consulta manual volvió a abrir correctamente. Consola revisada sin errores. Se guardó `RedVida-alerta-computadora.png`. Estas comprobaciones de pestañas son adicionales a las suites anteriores; no son una prueba de iPhone físico.

Si se usa otro navegador de computadora que permanecía abierto desde antes: recargar ambas páginas con Ctrl+Shift+R una vez y verificar que aparece el bloque RedVida Alerta. Abrir `http://localhost:8080/index.html` y `http://localhost:8080/sinapred.html` del mismo receptor. Un evento viejo sin aviso publicado no se convierte retroactivamente en alerta: iniciar otro ejercicio explícito.
