/* Punto de integración futura: configurar solo tras verificar endpoint, nombre de
   capa, CRS, licencia de reutilización y CORS mediante GetCapabilities público.
   No se inventa URL WMS/WMTS a partir del visor MapStore.
   Visor consultado: https://servidormapas.ineter.gob.ni/mapstore/#/viewer/openlayers/53
   Resultado de la consulta de desarrollo: 502; ninguna capa o licencia verificada.
   No se integra cartografía oficial ni densidad poblacional en esta versión. */
window.RedVidaMapConfig={officialLayer:null,populationLayer:null};
