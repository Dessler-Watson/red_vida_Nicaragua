# Créditos de recursos visuales

Recursos guardados localmente para que la interfaz no dependa de un CDN durante el uso sin conexión. Las fotografías son imágenes ilustrativas de archivo; no representan reportes recibidos ni eventos actuales en Nicaragua. Seleccionadas e inspeccionadas visualmente el 16 de octubre de 2026.

## Fotografías

Licencia de todas las fotografías: [Pexels License](https://www.pexels.com/license/). Se permite el uso y la modificación; no se implica aval de autores ni de personas representadas. Copias reducidas y convertidas a WebP, lado mayor 800 px, calidad 82.

| Archivo | Contenido observado | Autor y fuente |
|---|---|---|
| images/inundacion.webp | Calle inundada, vehículo parcialmente sumergido y peatones | Sveta K — [Flood on Street](https://www.pexels.com/photo/flood-on-street-8568719/) |
| images/terremoto.webp | Fachada dañada, hueco de ventana con escombros; blanco y negro | Serkan Gönültaş — [Demaged Building after an Earthquake](https://www.pexels.com/photo/demaged-building-after-an-earthquake-16632532/) |
| images/deslizamiento.webp | Ladera boscosa erosionada con suelo y raíces expuestas; no muestra un deslizamiento en movimiento | Elina Volkova — [Landslide in a Forest](https://www.pexels.com/photo/landslide-in-a-forest-16468555/) |
| images/tormenta.webp | Tormenta eléctrica con rayos bajo nubes oscuras; no es una foto de un huracán | Ndumiso Mvelase — [Intense Thunderstorm with Dramatic Lightning](https://www.pexels.com/photo/intense-thunderstorm-with-dramatic-lightning-31130767/) |

Archivos originales servidos por Pexels: `https://images.pexels.com/photos/ID/pexels-photo-ID.jpeg?auto=compress&cs=tinysrgb&w=800`, con los ID 8568719, 16632532, 16468555 y 31130767 respectivamente.

`images/otro.svg`: ilustración vectorial original realizada para RedVida Nicaragua. Representación abstracta de protección y terreno, no un mapa ni una fotografía documental.

## Tipografía

- `fonts/inter-latin.woff2`: Inter variable normal, pesos 100–900; Rasmus Andersson, [Google Fonts / Inter](https://fonts.google.com/specimen/Inter). Licencia SIL Open Font License 1.1 en `fonts/Inter-OFL.txt`.
- `fonts/manrope-latin.woff2`: Manrope variable normal, pesos 200–800; Mikhail Sharanda y colaboradores, [Google Fonts / Manrope](https://fonts.google.com/specimen/Manrope). Licencia SIL Open Font License 1.1 en `fonts/Manrope-OFL.txt`.
- Subconjuntos latinos incluyen caracteres españoles (á, é, í, ó, ú, ü, ñ). `fonts/source.css` conserva la respuesta de origen de Google Fonts; la interfaz debe cargar exclusivamente las copias locales.

## Iconos

`vendor/lucide.min.js`: Lucide 0.468.0 UMD, descargado de https://unpkg.com/lucide@0.468.0/dist/umd/lucide.min.js. Licencia ISC en `vendor/lucide-LICENSE.txt`; [proyecto oficial](https://lucide.dev/).

API global: `lucide.createElement(lucide.icons.House)` devuelve un SVG DOM; `lucide.createElement(lucide.icons.House).outerHTML` permite insertarlo en plantillas. Las definiciones de icono tienen forma `[tag, atributos, hijos]`. También disponible `lucide.createIcons()` para elementos `data-lucide`.
