/* Mismo origen: el receptor real se inicia con servidor.py.
   Para otra web se debe acordar este contrato y configurar aquí su URL HTTPS.
   No se envían datos a servicios de terceros ni ejemplos automáticamente. */
globalThis.RedVidaSyncConfig=Object.freeze({enabled:true,endpoint:'/api/reports',inbox:'/api/reports',receiverName:'Servidor RedVida',timeoutMs:15000});
