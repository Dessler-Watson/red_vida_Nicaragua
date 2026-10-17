> Actualización: el flujo de inicio y pantalla roja se describe en [ALERTA_ROJA.md](ALERTA_ROJA.md). Iniciar publica un ejercicio explícito sin verificar científicamente las señales.

# RedVida Alerta — diseño de la propuesta y guía de demostración

## Idea para el reto 09

**RedVida Alerta convierte señales colaborativas y solicitudes de ayuda en información explicable para organizar la respuesta post-emergencia.** La señal inicial orienta dónde verificar; los reportes de heridos, personas atrapadas, comunidades aisladas y necesidades ayudan al operador a decidir dónde concentrar recursos limitados. Detectar movimiento no demuestra daños ni justifica por sí solo un despacho.

El recorrido es: señales → candidato → revisión del operador → aviso ciudadano de prueba → solicitudes asociadas → prioridad justificada → asignación y seguimiento. Las entidades consultarían un mismo expediente territorial con trazabilidad. En este prototipo los perfiles institucionales son ficticios y no hay conexión oficial.

La idea se inspira en el principio de combinar señales de distintos teléfonos que explica [Google sobre Android Earthquake Alerts](https://blog.google/products-and-platforms/platforms/android/earthquake-detection-and-alerts/). RedVida no está integrada con Google, no utiliza sus servidores ni accede a sensores reales. No se ha implementado detección sísmica validada.

## Qué se implementó

- Sección «Eventos sísmicos» en el administrador.
- Dispositivos ficticios con coordenadas aproximadas, hora de detección y estado; animaciones y mapa Leaflet sobre cuadrícula local, sin teselas externas.
- Configuración de dispositivos (1–50), coincidencias mínimas (2–50), ventana temporal (1–120 s) y radio ancla (0,1–50 km). Todos son parámetros demostrativos.
- Eventos y acciones idempotentes guardados en SQLite, conservando la tabla original de reportes.
- Candidato automático sin alerta automática. Revisión humana de demostración necesaria antes de publicar.
- Aviso ciudadano destacado, señal sonora con activación explícita, intento de notificación del sistema cuando esté permitido y vibración si la plataforma la admite.
- Registro atómico del identificador de aviso para evitar repeticiones en pestañas del mismo origen. Las alertas se consultan periódicamente al servidor; BroadcastChannel no transmite este canal entre equipos.
- Historial, prioridad del operador, asociación de reportes y perfiles institucionales ficticios.
- Reutilización de inventario, asignaciones y reportes existentes. No se marca una necesidad como cubierta solo por asociar un recurso.

## Estados y reglas

| Estado | Interpretación |
|---|---|
| Señales recibidas | Se almacenaron señales sintéticas; puede no existir coincidencia suficiente. |
| Posible evento detectado | La regla demostrativa encontró una agrupación; queda registrado en el historial. |
| Pendiente de verificación | Existe candidato, sin autorización para difundir. |
| Confirmado en la simulación por el operador | Revisión de demostración; no equivale a confirmación científica o institucional. |
| Evento cerrado | No acepta más señales ni nuevas difusiones. Su historial se conserva. |

**Agrupación:** se buscan dispositivos distintos dentro de un radio respecto a una señal ancla y una ventana temporal móvil. Repetir el mismo dispositivo no aumenta las coincidencias. El radio ancla no es una estimación de epicentro ni de área real de daños; el diámetro del grupo puede ser mayor que ese radio. No se estima magnitud, intensidad ni tiempo hasta la llegada de ondas.

**Prioridad de coordinación (demostrativa):** Alta si hay reportes asociados con heridos o atrapados; Por evaluar si no hay reportes o faltan cantidades; Media si hay necesidades sin recurso asociado; Baja si no hay indicadores suficientes registrados. El operador puede modificarla, registrar una justificación y consultar el historial. La falta de GPS no reduce la gravedad. Estas reglas no constituyen triage clínico ni un protocolo sísmico oficial.

## Servidor y almacenamiento

Se reutiliza `servidor.py` con su misma SQLite:

- `GET /api/demo-events`: últimos 50 eventos y sus historiales.
- `POST /api/demo-events`: acciones `create`, `signals`, `review`, `publish`, `link_report`, `priority`, `close`, `receipt`.
- Cada POST lleva `eventId`, `actionId`, `demonstration: true` e `Idempotency-Key` igual a `actionId`. Repetir exactamente una acción devuelve su respuesta original; cambiar su contenido conservando el identificador se rechaza.
- Tablas nuevas: `demo_events`, `demo_event_actions`. La tabla `reports` y el contrato `/api/reports` se conservan.
- El servidor asigna `source: simulation` (compatible con eventos previos `synthetic-simulator`), `demonstration: true`, identificación y estados a todos los eventos. Las señales requieren `synthetic: true`.
- Una alerta publicada conserva un único identificador aunque se repita la solicitud de difusión. Los destinatarios se muestran como disponibles en una consola ficticia, nunca como entregados a instituciones reales.
- La PWA guarda una copia de eventos y avisos ya vistos en una base IndexedDB separada, `redvida-alerta`, sin cambiar `redvida-nicaragua` ni la cola de reportes.
- Acciones de operador cuya respuesta se perdió se conservan temporalmente en sessionStorage de esa pestaña. «Reintentar acción pendiente» reutiliza el mismo identificador; no se ejecutan como si se hubieran guardado.
- Inventario, revisiones de reportes y asignaciones continúan siendo locales al navegador del operador, según la arquitectura previa. No hay coordinación de inventario multioperador en el servidor.

## Cómo ejecutar la demostración completa

1. Iniciar `iniciar.ps1` desde la carpeta RedVida Nicaragua. Abrir `http://localhost:8080/sinapred.html` y `http://localhost:8080/index.html`.
2. En la PWA, buscar el bloque RedVida Alerta al final de la pantalla. Pulsar **Probar sonido**. Para intentar notificaciones del sistema, pulsar **Activar notificaciones** y decidir el permiso solicitado por el navegador.
3. En el administrador, abrir **Eventos sísmicos**. Usar, por ejemplo, 8 dispositivos, 3 coincidencias, 10 s y 2 km: son valores de demostración, no umbrales científicos.
4. Pulsar **Iniciar simulación**. Se publica inmediatamente un aviso de ejercicio y se muestran las señales; el candidato sigue sin verificar. **Detener** pausa la generación; **Reiniciar simulación** cierra el evento seleccionado y comienza otro, sin borrar el historial. Salir de la sección también detiene la generación.
5. Pulsar **Revisar y confirmar simulación** para registrar la revisión del candidato. El ejercicio iniciado ya tiene su aviso publicado; no necesita otro clic para llegar a la PWA. **Simular alerta ciudadana** sigue disponible para eventos anteriores sin aviso. El operador debe esperar a que termine cada guardado.
6. La PWA consulta el receptor cada 4 s mientras el navegador permite ejecutar la página. Al recibir el aviso, muestra un diálogo y un banner. El sonido depende de que el audio de esa sesión esté habilitado y no suspendido. Cada identificador se presenta automáticamente una sola vez por almacenamiento/origen del navegador; se puede consultar manualmente otra vez.
7. En el aviso, pulsar **Crear solicitud de ayuda de prueba**. Se prepara el formulario con coordenadas ilustrativas y fuente ficticia; estas solicitudes permanecen de prueba. Revisar datos, indicar cantidades/necesidades conocidas y guardar.
8. El reporte de prueba no se transmite automáticamente. En **Mis reportes → detalle**, autorizar **Enviar prueba al receptor RedVida**. Después el administrador podrá importarlo. También se puede autorizar el envío al asociar una prueba local desde el administrador.
9. Seleccionar el evento y asociar ese reporte. Revisar recomendación y guardar la prioridad justificada del operador.
10. Pulsar **Consultar reporte y asignar recursos**, elegir un recurso ficticio y cantidad, revisar y confirmar la asignación local. Regresar al simulador para ver recursos, asignaciones y necesidades sin recurso asociado.
11. Recargar: los eventos, vínculos, prioridad e historial se recuperan del servidor; las asignaciones se conservan en ese navegador. Los avisos ya vistos no deben volver a sonar automáticamente.

Entre teléfonos distintos se necesita acceder al mismo receptor HTTPS, con conexión y el acceso autorizado. `localhost` en un teléfono apunta al propio teléfono. El enlace temporal de prueba puede cambiar. La difusión es una consulta real a este receptor de desarrollo; las señales, eventos y destinatarios siguen siendo simulados.

## Offline, sonido y aplicación cerrada

La interfaz, los reportes y los eventos previamente almacenados pueden consultarse sin conexión después de preparar la caché. **No llegan alertas remotas nuevas sin comunicación con el receptor.** Reproducir audio en una página abierta no es un mecanismo de entrega con la app cerrada; el navegador puede suspender audio, temporizadores y consultas en segundo plano.

El módulo intenta `ServiceWorkerRegistration.showNotification` solo si el sistema lo admite y el usuario concedió permiso mediante el botón. No existe una suscripción Push ni un emisor Web Push configurado en esta entrega. No se instala un falso temporizador para prometer avisos después de cerrar la app.

Para Web Push real hacen falta: dirección HTTPS estable, suscripción del dispositivo, almacenamiento seguro de suscripciones, claves/configuración del emisor, autorización por roles y zona, expiración de avisos, registro de reintentos y pruebas reales de entrega. Apple documenta notificaciones para [web apps añadidas a la pantalla de inicio de iOS](https://webkit.org/blog/13878/). El modo silencio, Enfoque y ajustes del sistema pueden limitar avisos y sonido. Las [alertas críticas que pueden superar esos modos](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.usernotifications.critical-alerts) requieren capacidades nativas especiales aprobadas por Apple; este prototipo no las tiene.

## Ruta viable de evolución

1. **Demostración actual:** señales sintéticas, revisión humana, distribución conectada por consulta, reportes offline y coordinación con recursos ficticios.
2. **Piloto operativo:** backend con roles, inventario compartido, HTTPS estable, Web Push y suscripciones, auditoría de entregas, vencimiento de avisos, acuerdos y validación con equipos competentes. Mantener separación entre recomendaciones y decisiones humanas.
3. **Investigación de sensores:** evaluación por especialistas, datos etiquetados, falsos positivos/negativos, privacidad, consumo y restricciones móviles. Usar ubicación aproximada y consentimiento; nunca convertir el movimiento cotidiano de un teléfono en una alerta oficial. No se promete anticipación sísmica hasta validar el sistema.

La utilidad para el reto 09 se debe medir con tiempo de revisión y primera asignación, necesidades pendientes, trazabilidad, información faltante y duplicados evitados; no con una precisión de detección inventada.

## Archivos añadidos y modificados

Añadidos: `alertas.py`, `js/alerta-core.js`, `js/alerta-admin.js`, `js/alerta-ciudadano.js`, `css/alerta.css`, `tests/test_alertas.py`, `tests/alerta-test.html`, `tests/alerta-test.js` y este documento.

Modificados: `servidor.py`, `index.html`, `sinapred.html`, `js/ciudadano.js` (preparación de ayuda ficticia y etiquetas de coordenadas), `js/sinapred.js` (nueva sección), `sw.js` (precache y apertura de notificación), `tests/audit.js`, `README.md`.

No se reemplazaron el diseño ciudadano, `js/storage.js`, `js/sync.js`, IndexedDB de reportes ni la tabla de reportes.

## Pruebas y límites de validación

- 13 pruebas Python: 8 del receptor previo y 5 del canal de alertas. Se verificaron agrupación espacial/temporal, duplicados de dispositivos/acciones, rechazo de difusión previa a revisión, estados, historial, asociación, prioridad y persistencia.
- 8 pruebas del canal en navegador: reclamo atómico de avisos, pérdida de respuesta después del guardado, reintento idempotente, candidato sin publicación automática, bloqueo previo a revisión, único aviso simulado, cierre sin alterar reportes y caché de recursos.
- Regresión de almacenamiento y flujo previo: 15 pruebas de esquema, identificadores, persistencia y recursos.
- Regresión de sincronización de reportes: 6 pruebas, incluyendo respuesta perdida, mismo recibo/sin duplicados, exclusión de ejemplos, importación y envío automático.
- Flujo visual probado desde administrador en localhost y ciudadano en 127.0.0.1, con almacenamiento separado: 8 señales, candidato, revisión, publicación, recepción, solicitud ficticia, transmisión autorizada, vínculo, prioridad, asignación de 10 litros y recuperación tras recarga.
- Controles manuales: reiniciar creó otro identificador y conservó el evento anterior; detener mantuvo el conteo estable (11 señales). Con el receptor de laboratorio apagado, la PWA abrió desde caché y permitió consultar el aviso almacenado. Esta prueba no equivale a modo avión en un iPhone físico.
- La activación del motor AudioContext y la emisión programada al llegar un aviso nuevo se observaron en el navegador. La audibilidad física, volumen y comportamiento en iPhone real siguen pendientes. La prueba de notificación visual pasó; notificación del sistema/permiso real, vibración y apertura desde una notificación real no se comprobaron en hardware.
- No se han probado sensores reales (no existen en el módulo), precisión sísmica, entrega Push con la app cerrada, integración institucional, alertas críticas ni distribución sin internet.

Total automatizado: 42 comprobaciones correctas (13 Python, 8 alertas, 15 almacenamiento y 6 sincronización).

Para las pruebas automatizadas usar el puerto 8081 con `--allow-tests` y una base separada, tal como indica el README. Los fixtures son ficticios; nunca representan una emergencia real.
