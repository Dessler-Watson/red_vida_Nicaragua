# RedVida — alerta clara de emergencia

Se reemplazó la composición de la alerta, conservando la PWA y su funcionamiento. La vista principal utiliza tres zonas: cabecera #E52335 con triángulo SVG de 116 px, datos compactos sobre blanco y protección breve con acción roja. No hay tarjetas grises oscuras ni fondo granate. El identificador se consulta en un desplegable y puede copiarse.

En 360 × 800 la cabecera mide aproximadamente 266 px (un tercio de la pantalla). El botón Informar daños y pedir ayuda termina aproximadamente en el píxel 695: se ve completo sin desplazar. Magnitud, ubicación, hora y Mantén la calma están encima. Estos datos se leen del evento; no son cifras fijas ni mediciones de teléfonos. El estado continúa separado de una alerta oficial.

Se conservaron Qué debo hacer, formulario de informe, GPS por permiso, sonido y vibración, notificación del sistema según compatibilidad, acuses, deduplicación, Python/SQLite, IndexedDB y cola offline. El receptor es RedVida, sin recepción institucional real. El formulario y las instrucciones usan ahora fondo claro también. La entrada anima el símbolo una vez y lo pulsa dos veces; las ondas y la luz son finitas. La reducción de movimiento desactiva las animaciones. Se aislaron reglas globales de header/details/dialog que distorsionaban el contenido.

## Archivos

Modificados: js/alerta-ciudadano.js (composición y copiar ID), css/alerta.css (reemplazo del estilo del módulo), index.html, sinapred.html, sw.js (caché versión 40), tests/alerta-test.js y tests/audit.js (referencias de caché), README.md. Sin cambios en contratos de eventos, servidor, almacenamiento ni cola.

## Pruebas ejecutadas

- Evento iniciado desde administrador localhost:8081 y recibido por consulta en 127.0.0.1:8081: nueva pantalla, magnitud 5.8, zona, hora e ID procedentes del evento.
- Validación real a 360 × 800, con captura de pantalla y medición del botón: íntegro en primera pantalla. Triángulo vectorial de 116 px.
- Anchos solicitados 320, 360, 390 y 430, alto 800: sin desbordamiento horizontal. Tamaños efectivos del navegador 321/360/390/431. Botón principal termina entre 647 y 695 px.
- Copiar ID confirmó ID copiado. Panel de instrucciones abrió tres etapas y regresó a la alerta.
- Formulario desde Informar daños y pedir ayuda: informe ficticio RVN-2026-AF5F0D635F1744A39DFBC7D799209B32 recibido por servidor RedVida y vinculado al evento. El administrador mostró un reporte asociado con heridos; no se solicitaron coordenadas reales en esta prueba.
- Reconocer y recargar no reabrió el diálogo. No se borraron eventos ni informes. Consola revisada sin errores JavaScript.
- Regresión: 14 Python, 8 canal/caché, 15 IndexedDB/recursos y 6 sincronización. Total 43 comprobaciones correctas en las ejecuciones finales.
- Animación calculada: una entrada y dos pulsaciones. Estilos de movimiento reducido implementados; no es una prueba clínica de fotosensibilidad.

Los ensayos se hicieron con base separada en 8081. No se probaron hardware iPhone, audibilidad física, vibración real, permisos/notificación del sistema ni Web Push cerrado en esta revisión visual. Se conservan sus límites previos. Los eventos remotos nuevos requieren conexión; los informes pendientes usan la cola existente.

## Abrir

App: http://localhost:8080/index.html. Administrador: http://localhost:8080/sinapred.html → Eventos sísmicos. Mantener el receptor Python iniciado. Recargar pestañas antiguas con Ctrl+Shift+R una vez para recibir los recursos actuales.
