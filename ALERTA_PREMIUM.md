# RedVida — alerta sísmica premium

Se rediseñó la vista superpuesta existente, sin reemplazar la PWA, IndexedDB, el receptor Python/SQLite, la cola de reportes ni los identificadores.

## Interfaz

Cabecera con logo local y hora real del evento; distintivo permanente SIMULACIÓN; triángulo vectorial blanco; dos pulsaciones y ondas finitas; fondo rojo oscuro/carbón; tipografías Manrope e Inter locales. La vista queda estable después de la entrada. Se respeta `prefers-reduced-motion` y no hay parpadeo rápido ni animación infinita.

El título va en dos líneas y muestra una indicación inmediata de protección. La tarjeta usa magnitud, zona, fecha, estado e ID del objeto de evento. Faltan datos: Sin dato o Ubicación no disponible. No se estiman magnitudes con teléfonos. La sección Mantén la calma contiene instrucciones breves; Qué debo hacer abre tres etapas sin recargar la PWA. Detener señal local cancela osciladores y vibración disponibles. Entendido cierra sin borrar el evento, los reportes ni la comunicación.

## Informe compacto

Informar a las autoridades abre un formulario en la misma superposición. Permite movimiento, daños, cantidades heridas/atrapadas (vacías = información desconocida), necesidades, descripción y referencia. GPS se solicita solo con el botón y permiso; no se copian como GPS las coordenadas sintéticas del escenario. El nombre no es obligatorio en este informe. Todos los informes del ejercicio conservan fuente demo, claramente visible.

Guardar y enviar informe de prueba autoriza expresamente la transmisión al receptor RedVida, no a instituciones. Reutiliza `RedVidaStorage.saveReport`, `enqueueReport(...allowDemo:true)` y `RedVidaSync.flush`. El ID se conserva en reintentos y el botón se bloquea al guardar. Si falla la comunicación, el informe permanece local y en la cola existente; no se presenta como recibido.

Después del recibo válido se intenta vincular con el evento mediante la ruta existente `/api/demo-events`, acción link_report. La intención y su actionId se conservan localmente para reintentar sin duplicar vínculos, incluso tras recargar. El administrador importa el informe mediante su mecanismo previo y lo muestra en coordinación. Si el evento ya se cerró, el informe se conserva y se explica que el vínculo no pudo guardarse; no se simula éxito.

Estados mostrados: guardando, guardado localmente/pendiente, enviando cuando la cola lo acredita y recibido solo con recibo real. El seguimiento continúa mientras la PWA/navegador permite ejecutar la cola, con las mismas limitaciones previas de iOS.

## Pruebas ejecutadas

- 14 Python, 8 del canal/caché, 15 de IndexedDB/recursos y 6 de sincronización: 43 correctas, 0 fallos en las ejecuciones finales.
- Administrador localhost:8081 y ciudadano 127.0.0.1:8081: el clic de inicio abrió la vista nueva a través del servidor, con almacenamientos separados.
- Evento EVT-E6A3C2FF50CD4AE7AF9B59A86B719D41: magnitud 5.8 y zona del escenario; formulario online RVN-2026-469C14E2BF6B482893CF72A4BC9D7C6C confirmado y vinculado.
- Con el receptor de laboratorio apagado: RVN-2026-B883034AEF3640499876605F50B5D13D permaneció guardado/pendiente. Al reiniciarlo se recibió y vinculó. Ambos IDs aparecieron una sola vez en la respuesta del servidor y el administrador mostró dos informes vinculados.
- Un segundo evento configurado con magnitud 6.3 y otra zona mostró exactamente esos datos: no hay cifra fija. Reconocer/recargar no reabrió el evento anterior; uno nuevo sí.
- Instrucciones, regreso, formulario y cierre funcionaron; la navegación normal permanece debajo del diálogo.
- Anchos solicitados 320, 360, 390 y 430: sin desbordamiento horizontal en alerta; formulario revisado en 320 y 430. Algunos tamaños efectivos del navegador resultaron 321 y 431 px. Animación calculada: entrada una vez, pulso dos veces. Reducción de movimiento implementada por CSS.
- Caché actual incluye el nuevo módulo del formulario; consola revisada sin errores JavaScript. No se solicitó ubicación real durante las pruebas.

Prueba de receptor apagado equivale a pérdida del servidor, no a modo avión físico. No se comprobaron audibilidad física, vibración del iPhone, permiso/notificación real del sistema, Web Push cerrado ni hardware de sensores. Se conserva el mecanismo anterior de audio/vibración/notificación; no se amplían sus garantías. No existe envío institucional real.

## Archivos

Añadido `js/alerta-report.js`. Modificados `js/alerta-ciudadano.js`, `css/alerta.css`, `index.html`, `sinapred.html`, `sw.js` (versión 38), `tests/alerta-test.js`, `tests/audit.js` y `README.md`. Sin cambios en `servidor.py`, `alertas.py`, `js/storage.js`, `js/sync.js` ni sus esquemas.

## Abrir

Iniciar el receptor del proyecto mediante la tarea VS Code Ctrl+Shift+B o iniciar.ps1. Ciudadano: http://localhost:8080/index.html. Administrador: http://localhost:8080/sinapred.html → Eventos sísmicos. Recargar pestañas antiguas una vez. Los fixtures se ejecutaron en 8081 con base separada; el servidor principal mantiene sus datos.
