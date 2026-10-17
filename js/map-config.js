/* Punto de integración: configuración del mapa del panel de operaciones.
   ------------------------------------------------------------------------
   BASE CARTOGRÁFICA (window.RedVidaMapConfig.basemap)
   - provider 'esri' (predeterminado): Esri World Light Gray Canvas.
     Sin API key, sin registro. Probado: responde tiles reales z7–z16.
   - provider 'carto': CARTO Positron (estilo claro, igual que antes).
     Desde el 25/09/2026 los tiles raster de CARTO exigen ?key=...
     Key GRATIS y sin cuenta: https://carto.com/basemaps/apikey/
     (llega por correo en ~1 min; 5M peticiones/mes sin fines comerciales).
     Pasos: copia la key, pégala en cartoKey y cambia provider a 'carto'.
   ------------------------------------------------------------------------
   Capas oficiales INETER: ninguna integrada. El visor consultado
   (https://servidormapas.ineter.gob.ni/mapstore/#/viewer/openlayers/53)
   devolvió 502; ninguna capa o licencia verificada. No se inventa URL
   WMS/WMTS a partir de un visor. officialLayer y populationLayer quedan
   en null hasta verificar endpoint, nombre de capa, CRS, licencia y CORS. */
window.RedVidaMapConfig={
  officialLayer:null,
  populationLayer:null,
  basemap:{
    provider:'esri',
    cartoKey:'',
    esri:{
      name:'Esri · lienzo claro',
      label:'ESRI · OPENSTREETMAP',
      url:'https://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}',
      maxZoom:19,
      attribution:'© <a href="https://www.esri.com/">Esri</a>, HERE, Garmin, FAO, NOAA, USGS, © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    },
    carto:{
      name:'CARTO Positron · online',
      label:'CARTO POSITRON · OPENSTREETMAP',
      url:'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
      subdomains:'abcd',
      maxZoom:19,
      attribution:'© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · © <a href="https://carto.com/attributions">CARTO</a>'
    }
  }
};
