# Informe del proyecto RedVida Nicaragua

## 1. Identificación del proyecto

**Nombre:** RedVida Nicaragua  
**Propósito:** apoyar el registro, recepción, verificación y priorización de necesidades después de una emergencia.  
**Reto:** 09 - Optimización y priorización de recursos y esfuerzos en la post-emergencia.  
**Tipo de entrega actual:** prototipo funcional web progresivo (PWA), con aplicación ciudadana, panel administrativo y receptor local de desarrollo.  
**Estado:** demostración funcional en localhost, preparada para evolucionar hacia un piloto con backend institucional.

RedVida no sustituye las decisiones de SINAPRED, alcaldías, cuerpos de rescate ni personal sanitario. Su objetivo es ordenar información fragmentada para que las autoridades puedan revisar mejor, decidir más rápido y dejar trazabilidad de cada acción.

## 2. Problema que se aborda

Después de un terremoto, inundación, deslizamiento u otro evento severo se presentan simultáneamente:

- múltiples solicitudes de ayuda en zonas distintas;
- cortes de comunicación y conectividad intermitente;
- rutas bloqueadas y dificultad para conocer la situación territorial;
- cantidades de personas afectadas incompletas o cambiantes;
- recursos limitados que deben asignarse con rapidez;
- información duplicada, desactualizada o difícil de comparar;
- presión para actuar antes de contar con un diagnóstico completo.

El problema central no es únicamente recibir reportes. Es convertir reportes incompletos y señales dispersas en una cola de atención que explique qué se debe revisar primero, qué información falta y qué recurso puede asignarse sin ocultar las incertidumbres.

## 3. Solución propuesta

RedVida conecta dos experiencias bajo el mismo receptor:

1. **Aplicación ciudadana:** permite informar una emergencia con un formulario breve, ubicación GPS opcional o referencia manual, daños, personas afectadas y necesidades.
2. **Panel de coordinación:** permite consultar reportes, ver su ubicación cuando existe, revisar prioridades, asociar necesidades a eventos, asignar recursos y seguir la evolución del caso.
3. **Módulo Eventos sísmicos:** permite ejecutar desde el administrador un ejercicio controlado de señales colaborativas y publicar un aviso de prueba para comprobar el flujo de comunicación.
4. **Receptor RedVida:** guarda en SQLite los reportes recibidos, conserva acuses y evita duplicados mediante identificadores estables e idempotencia.

El flujo de apoyo a la decisión queda organizado así:

```text
Señales colaborativas
        ↓
Posible evento / zona que requiere verificación
        ↓
Reportes ciudadanos y necesidades
        ↓
Revisión humana y prioridad explicable
        ↓
Asignación de recursos y seguimiento
        ↓
Historial auditable para coordinación post-emergencia
```

Una señal de movimiento orienta dónde verificar; no se interpreta por sí sola como prueba de daños, epicentro ni autorización de despacho.

## 4. Funciones implementadas

### 4.1 Aplicación ciudadana

- Interfaz móvil responsive con diseño orientado a uso rápido bajo presión.
- PWA instalable con manifest, Service Worker y recursos locales.
- Formulario de reporte por pasos con nombre completo, tipo de desastre, ubicación, descripción, afectaciones y necesidades.
- GPS opcional mediante permiso del navegador.
- Referencia manual cuando no se dispone de GPS.
- Validación de cantidades enteras y límites razonables.
- Identificador único estable para cada reporte.
- Guardado local en IndexedDB antes de intentar cualquier transmisión.
- Cola local `outbox` para conservar envíos pendientes.
- Reintentos automáticos al recuperar conexión, manteniendo el mismo identificador.
- Historial y búsqueda de reportes guardados.
- Estados visibles: pendiente, intentando enviar, requiere revisión o recibido por el servidor RedVida.
- Aviso claro cuando el reporte sólo está guardado localmente.
- Consulta de eventos previamente almacenados cuando la conexión se pierde.
- Formulario de daños y solicitud de ayuda asociado a un aviso de prueba.
- Diseño de alerta roja, sonido mediante activación explícita, vibración si el dispositivo lo permite y notificación del sistema cuando el navegador la autoriza.
- El ciudadano no inicia ejercicios sísmicos: la creación de eventos queda en el administrador.

### 4.2 Panel administrativo

- Panel profesional para SINAPRED/coordination center en `sinapred.html`.
- Lectura del receptor RedVida y de los reportes locales del navegador operador.
- Tabla de reportes con búsqueda, filtros y estados.
- Mapa con marcadores únicamente cuando el reporte tiene coordenadas válidas.
- Apertura del detalle correcto desde cada marcador.
- Revisión de prioridad, urgencia, peligro inmediato, aislamiento y seguimiento.
- Registro de notas y cambios operativos.
- Inventario de recursos y disponibilidad.
- Asignación de recurso, cantidad y unidad a un reporte.
- Liberación de asignaciones y actualización de existencias.
- Historial local de actividad y decisiones.
- Importación idempotente: el mismo reporte recibido no se agrega dos veces.
- Separación visible entre reportes ciudadanos y ejercicios de prueba.

### 4.3 Eventos sísmicos y señales colaborativas

El módulo se llama **Eventos sísmicos** y sólo puede iniciarse desde el administrador.

- Configuración demostrativa de dispositivos, coincidencias mínimas, ventana temporal, radio y zona.
- Señales con hora, ubicación aproximada y dispositivo identificable.
- Agrupación temporal y espacial de dispositivos distintos.
- Prevención de que repetir un dispositivo aumente artificialmente la coincidencia.
- Historial de señales, candidato, revisión, publicación, vínculos y cierre.
- Publicación de un aviso de prueba con un identificador estable.
- Consulta periódica de nuevos avisos mientras la aplicación está abierta y conectada.
- Deducción de alertas repetidas entre pestañas del mismo origen.
- Acciones idempotentes para no duplicar eventos ni cambios.
- El aviso de prueba conserva una presentación claramente diferenciada de una alerta oficial.

### 4.4 Receptor y persistencia

- `servidor.py` sirve los archivos estáticos y expone la API de desarrollo.
- SQLite conserva reportes recibidos y eventos del módulo sísmico.
- `POST /api/reports` recibe reportes con `Idempotency-Key`.
- `GET /api/reports` permite al administrador consultar lo almacenado.
- `GET/POST /api/demo-events` gestiona eventos y acciones del ejercicio.
- El servidor confirma sólo después de guardar correctamente.
- Repetir un envío idéntico devuelve el mismo recibo.
- Reutilizar un ID con contenido diferente genera conflicto y conserva el primer contenido.
- IndexedDB versión 3 conserva reportes, operaciones y cola de salida.
- IndexedDB separada `redvida-alerta` conserva eventos y avisos ya vistos.

## 5. Cómo resuelve el reto 09

### 5.1 Orientación territorial inicial

El módulo de señales permite representar varios teléfonos que reportan movimiento en una zona. El sistema agrupa señales de dispositivos distintos por cercanía y tiempo, generando un candidato para revisión. Esto ayuda a concentrar la atención inicial donde existe una coincidencia, incluso si todavía no se tienen reportes completos.

La regla es deliberadamente prudente: una agrupación no se presenta como confirmación científica ni como cálculo de magnitud o epicentro. El operador debe revisarla antes de utilizarla para coordinar.

### 5.2 Captura de afectaciones con conectividad intermitente

La persona puede guardar un reporte sin conexión. El registro queda localmente con su ID, ubicación disponible, necesidades y estado pendiente. Cuando vuelve la conexión, la cola conserva el mismo contenido e intenta enviarlo de manera automática con el mismo identificador.

Esta decisión resuelve una causa importante de pérdida de información: el corte de red no elimina lo que la comunidad ya registró.

### 5.3 Priorización explicable

La prioridad recomendada se basa en indicadores disponibles, no en una puntuación opaca:

| Indicador | Efecto de coordinación |
|---|---|
| Personas heridas o atrapadas | Prioridad alta o urgente para revisión inmediata |
| Necesidades sin recurso asociado | Mantiene el caso visible como pendiente |
| Cantidades desconocidas | Solicita verificación; no interpreta el vacío como cero |
| Aislamiento o peligro inmediato | Aporta contexto para decidir el orden |
| Falta de GPS | No reduce la gravedad del caso |

El operador puede modificar la prioridad y debe registrar una justificación. Esto permite explicar por qué un caso se atendió antes que otro y revisar la decisión posteriormente.

### 5.4 Asignación racional de recursos

El panel relaciona la necesidad con un inventario disponible. Antes de confirmar una asignación valida que exista cantidad suficiente, descuenta existencias y crea un registro con recurso, cantidad, unidad, reporte y hora.

Así se evita asignar dos veces el mismo recurso disponible dentro del navegador operador y se conserva la diferencia entre una necesidad detectada y una necesidad realmente cubierta.

### 5.5 Seguimiento y trazabilidad

Cada reporte mantiene su ID, estado, acuse, cambios operativos, vínculos con eventos y asignaciones. El historial permite reconstruir:

- cuándo fue creado;
- cuándo se guardó localmente;
- cuándo se envió;
- cuándo el receptor confirmó la copia;
- qué prioridad se recomendó;
- qué cambió el operador;
- qué recurso se asignó o liberó.

La trazabilidad es útil para coordinar equipos, identificar información faltante y medir tiempos de respuesta.

## 6. Viabilidad técnica

La solución actual es viable como prototipo y piloto controlado porque utiliza tecnologías disponibles en navegadores modernos:

- HTML, CSS y JavaScript sin dependencia de un framework obligatorio.
- IndexedDB para persistencia local.
- Service Worker para caché de la interfaz y operación básica sin red.
- SQLite para recepción local de desarrollo.
- API HTTP sencilla que puede reemplazarse por un backend institucional.
- Diseño responsive para teléfono, tablet y escritorio.
- Leaflet y marcadores con coordenadas válidas; la base cartográfica externa se considera una dependencia separada.
- Identificadores UUID y claves de idempotencia para controlar reintentos.

La arquitectura permite evolucionar sin reconstruir la aplicación ciudadana: el contrato de reportes, la cola y el panel pueden conectarse a un backend autenticado cuando se definan los procesos institucionales.

## 7. Seguridad y honestidad del prototipo

- El receptor se ejecuta por defecto en loopback y no se publica automáticamente.
- La aplicación distingue guardado local de recepción confirmada por el servidor RedVida.
- No se afirma recepción real por SINAPRED.
- Los ejercicios se originan en el administrador y conservan marcas internas de prueba.
- No se mezclan silenciosamente ejemplos precargados con reportes ciudadanos.
- Los eventos sísmicos actuales no usan sensores reales, Google Earthquake Alerts ni servidores de Google.
- No existe Web Push configurado para prometer avisos con la aplicación cerrada.
- Las notificaciones, el sonido y la vibración dependen del navegador, permisos y sistema operativo.
- No se inventa una capa oficial de INETER ni una densidad poblacional oficial.
- El mapa base OpenStreetMap requiere conexión para descargar teselas; los datos del reporte permanecen disponibles sin ellas.

## 8. Pruebas realizadas

La auditoría del proyecto verificó:

- recepción y persistencia SQLite;
- acuse idempotente y rechazo de contenido conflictivo;
- solicitudes simultáneas sin duplicar reportes;
- validación de origen, campos y archivos privados;
- IndexedDB, identificadores y deduplicación;
- cola offline, reintentos y pérdida de respuesta después del guardado remoto;
- exclusión automática de ejercicios y ejemplos;
- importación de reportes al administrador sin duplicados;
- agrupación de señales, revisión, publicación, cierre y acciones idempotentes;
- asignaciones, inventario, liberación y recuperación después de recargar;
- diseño responsive en anchos móviles, tablet y escritorio;
- registro del Service Worker y carga desde caché;
- consola del navegador sin errores JavaScript en el flujo auditado;
- alerta visual, copia del ID, instrucciones, reconocimiento y no reapertura automática del mismo aviso.

La regresión final reunió **43 comprobaciones correctas** entre receptor, alertas, almacenamiento, caché, sincronización y flujo visual. La audibilidad física, vibración real, permisos de notificación en un iPhone real y entrega con la aplicación completamente cerrada requieren pruebas en hardware y un servicio de notificaciones real.

## 9. Funciones plenamente operativas en la demostración

- Registro ciudadano en el navegador.
- Guardado offline en IndexedDB.
- Generación y conservación de ID único.
- Cola de envío y reintentos al recuperar conexión.
- Receptor local Python/SQLite.
- Acuse real del receptor RedVida de desarrollo.
- Consulta del mismo reporte desde el administrador mediante la API.
- Filtros, búsqueda, detalle y mapa de coordenadas válidas.
- Revisión de prioridad y seguimiento.
- Inventario y asignaciones locales persistentes.
- Eventos sísmicos iniciados desde el administrador.
- Historial e idempotencia de eventos y acciones.
- Aviso de prueba visible en la PWA cuando el evento fue publicado.
- Caché offline de la interfaz y consulta de registros previamente almacenados.

## 10. Funciones simuladas o demostrativas

- Señales de teléfonos y agrupación colaborativa.
- Eventos sísmicos y aviso de prueba.
- Perfiles de instituciones y recursos del inventario.
- Coordenadas ilustrativas de escenarios precargados.
- Reglas de recomendación de prioridad.
- Sonido, vibración y notificación visual dentro de las capacidades del navegador.

Estas funciones sirven para explicar y evaluar el flujo de coordinación. No representan mediciones sísmicas reales ni despachos institucionales reales.

## 11. Funciones que requieren backend institucional

- Autenticación y roles para operadores, municipios y organismos de respuesta.
- Backend HTTPS público y base de datos central con copias de seguridad.
- Integración oficial con SINAPRED y acuerdos de intercambio de datos.
- Inventario compartido entre varios operadores.
- Sincronización de asignaciones y estados entre instituciones.
- Auditoría institucional, control de acceso y política de conservación de datos.
- Envío de reportes a canales oficiales y confirmación institucional.
- Escalamiento, zonas de responsabilidad y reglas operativas aprobadas.

## 12. Funciones que dependen de servicios externos

- Teselas de OpenStreetMap para el mapa base.
- Servicio cartográfico o geocodificación, si se decide incorporarlo.
- Web Push para avisos remotos con la aplicación en segundo plano o cerrada.
- Proveedor HTTPS, dominio y certificados para teléfonos fuera de la computadora local.
- Servicios oficiales de sensores o alertas sísmicas, únicamente después de validar integración, licencias y autorización.

## 13. Cómo ejecutar una demostración completa

1. Abrir la carpeta `C:\Users\User\Desktop\RedVida Nicaragua` en VS Code.
2. Iniciar el proyecto con `Ctrl+Shift+B` o ejecutar `iniciar.ps1`.
3. Abrir la aplicación ciudadana en `http://localhost:8080/index.html`.
4. Abrir el administrador en `http://localhost:8080/sinapred.html`.
5. En **Eventos sísmicos**, iniciar un evento de prueba y observar su historial.
6. En la aplicación ciudadana, revisar el aviso y abrir **Informar daños y pedir ayuda**.
7. Guardar el reporte; si el receptor está disponible, comprobar el acuse RedVida.
8. En el administrador, buscar el ID, abrir el detalle, revisar prioridad y asociar un recurso.
9. Recargar ambas interfaces y confirmar que el evento, reporte, prioridad y asignación permanecen.
10. Para la prueba offline, preparar primero la caché, desconectar la red, crear un reporte y comprobar que queda pendiente; después recuperar la conexión y verificar el envío automático sin crear un segundo reporte.

## 14. Próxima etapa recomendada

La siguiente etapa debe ser un piloto con backend seguro y usuarios autorizados. Antes de usarlo en una emergencia real conviene definir con SINAPRED el protocolo de validación, los niveles de prioridad, los responsables de confirmar información, el inventario compartido, el tratamiento de datos personales y los indicadores de éxito.

Los indicadores recomendados son:

- tiempo desde el primer reporte hasta la revisión;
- tiempo hasta la primera asignación;
- necesidades pendientes por zona;
- reportes duplicados evitados;
- porcentaje de casos con información incompleta;
- recursos asignados y liberados;
- tiempo de resolución por tipo de necesidad;
- trazabilidad completa de cada decisión.

## 15. Conclusión

RedVida transforma una situación de información fragmentada en un expediente de coordinación: conserva reportes cuando falla la conectividad, los identifica sin duplicarlos, los muestra territorialmente, propone un orden de revisión basado en indicadores comprensibles y registra qué recurso se asignó y por qué.

La propuesta es técnicamente viable como PWA y demostración local. Su valor para el reto 09 está en reducir el tiempo de organización y mejorar la trazabilidad bajo presión, manteniendo la decisión final en manos de operadores y autoridades. Para convertirse en una plataforma operativa nacional todavía necesita backend institucional, seguridad, integración oficial, validación de protocolos y pruebas en campo.

