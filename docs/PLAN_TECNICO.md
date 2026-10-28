# Plan técnico — Armador de Imágenes

## Requisito obligatorio: funcionamiento sin conexión

La aplicación debe funcionar completamente sin internet después de instalarse. El procesamiento de imágenes, la detección de solapamientos, la exportación, las vistas previas y cualquier mejora por IA deben ejecutarse localmente en el dispositivo. No se permiten servicios web, APIs remotas, cuentas, telemetría obligatoria ni descargas de modelos durante el uso normal.

Todos los ejecutables, bibliotecas, recursos y modelos necesarios se deben incluir en el instalador o paquete de la aplicación, o instalarse desde un paquete local distribuido junto con ella. El primer arranque y todas las funciones deben seguir funcionando con Wi-Fi y datos móviles desactivados. La descarga de herramientas para preparar el instalador puede requerir internet en el equipo de desarrollo, pero la aplicación instalada no debe necesitarlo.

La función de superresolución por IA solo se incluirá si el modelo y su motor pueden empaquetarse y ejecutarse localmente en Windows 7 de 64 bits y Android, con las licencias verificadas. Si un motor no es compatible con una plataforma, no se debe sustituir por un servicio en línea: se ofrecerá un método local compatible o se desactivará esa opción en esa plataforma.

## 1. Estrategia de arquitectura

Mantener tres capas separadas:

1. **Interfaz**: selección de carpetas/archivos, lista de parejas, vista previa, controles de corrección e informe.
2. **Núcleo de imágenes**: detección de márgenes, búsqueda de solapamiento, alineación, composición y exportación.
3. **Adaptadores de plataforma**: acceso a archivos y empaquetado para Windows y Android.

La interfaz no debe contener el algoritmo de ensamblado. El núcleo debe poder probarse con imágenes de ejemplo sin abrir la interfaz.

## 2. Emparejamiento por nombre

Convención inicial:

- `Arizona 1.png`: parte superior.
- `Arizona 2.png`: parte inferior.
- Resultado esperado: `Arizona.png`.

El emparejador debe aceptar extensiones comunes de imagen y nombres con espacios. Debe detectar parejas incompletas o nombres ambiguos y reportarlos, sin elegir archivos arbitrariamente.

## 3. Recorte de franjas negras

Cada captura se analiza independientemente, ya que las franjas laterales pueden tener grosores diferentes.

El detector debe identificar franjas exteriores continuas y conservar el contenido interior. No debe borrar píxeles oscuros que formen parte del documento. Se registrarán los límites de recorte para poder inspeccionarlos durante la revisión.

## 4. Unión vertical

- Buscar el solapamiento entre el final de la imagen superior y el comienzo de la inferior.
- Utilizar características visuales y comparación de regiones para estimar el desplazamiento vertical.
- Verificar que el emparejamiento sea coherente antes de unir.
- Evitar transformaciones geométricas innecesarias; las capturas de pantalla normalmente deberían poder alinearse mediante desplazamiento.
- Evitar suavizado y cambios de escala salvo que una necesidad real y confirmada lo requiera.

## 5. Revisión de resultados

Clasificar los resultados como:

- **Coincidencia clara**: generar la vista previa y permitir confirmación.
- **Dudoso**: detener la aceptación automática y mostrar una vista previa con controles para ajustar la unión.
- **Sin coincidencia suficiente**: dejar la pareja pendiente y explicar el motivo.

La aplicación no debe ocultar errores ni presentar como correcta una unión que no haya podido verificar.

## 6. Exportación, tamaño físico y mejora opcional

Después de unir y revisar cada pareja, la aplicación debe ofrecer tres variantes comparables, sin alterar el resultado base:

1. **Unión original**: guardar la composición con sus dimensiones en píxeles tal como quedó después del recorte y ensamblado, sin ampliación ni suavizado. Registrar 300 ppp solo si el usuario lo elige; cambiar los metadatos de ppp por sí solo no aumenta el detalle ni los píxeles.
2. **Tamaño de impresión 8.5 pulgadas a 300 ppp**: generar una copia de 2550 píxeles de ancho, con altura calculada proporcionalmente para conservar la relación de aspecto y asignar metadatos de 300 ppp. La ampliación convencional debe ser una opción diferenciada y no debe sobrescribir la unión original.
3. **Ampliación con superresolución por IA**: permitir generar una variante usando un modelo como Real-ESRGAN y después ajustar el resultado al ancho final de 2550 píxeles si hace falta. Debe ser opcional; los modelos de IA pueden inventar o modificar detalles finos, incluidos caracteres, líneas y pequeños símbolos.

Antes de guardar, mostrar vistas previas comparables de la unión original, la copia preparada para 8.5 pulgadas/300 ppp y la variante procesada por IA. Permitir ampliar la vista para inspeccionar texto pequeño y bordes. La vista previa no debe sustituir ni modificar el archivo base.

- Conservar la proporción original; nunca estirar la imagen para alcanzar un tamaño fijo de alto.
- Guardar el resultado de la unión sin pérdida, preferentemente PNG, para evitar artefactos JPEG en texto y bordes.
- Mantener los originales y la unión base intactos; guardar cada variante por separado.
- Tratar Windows 7 y Android como destinos separados al evaluar el motor de IA: verificar arquitectura, requisitos de GPU/Vulkan, memoria, tamaño de modelos, licencia y compatibilidad real antes de integrarlo.
- No prometer que una imagen será más fiel solo por tener más píxeles. El usuario debe poder comparar la variante con IA contra la original antes de aceptarla.

## 7. Procesamiento por lotes y seguridad

- Leer los originales sin modificarlos.
- Escribir resultados en una carpeta de salida separada.
- Producir un informe con archivos procesados, pendientes y errores.
- Permitir repetir el proceso sin sobrescribir originales.
- Controlar el uso de memoria para carpetas grandes.

## 8. Compatibilidad de plataformas

### Windows 7 de 64 bits

La compatibilidad con Windows 7 condiciona la selección de Python, Kivy y bibliotecas binarias. Se debe fijar una combinación de versiones compatible y probarla en Windows 7 real o en una máquina virtual antes de elegirla como versión de producción. No actualizar dependencias a ciegas si eso rompe el soporte de Windows 7.

### Android

El empaquetado Android requiere verificar que las dependencias del núcleo puedan compilarse e instalarse con la cadena de herramientas Android elegida. La selección de archivos debe funcionar con los mecanismos de almacenamiento disponibles en las versiones de Android que se decidan soportar.

## 9. Fases propuestas

1. Crear pruebas del emparejamiento por nombres.
2. Implementar y probar detección de franjas negras con anchos variables.
3. Implementar búsqueda de solapamiento y unión vertical.
4. Crear un conjunto de pruebas con capturas sintéticas y reales.
5. Añadir la interfaz de revisión y corrección manual.
6. Añadir procesamiento por lotes e informe.
7. Empaquetar y probar Windows 7 de 64 bits.
8. Empaquetar y probar Android.

## 10. Decisiones pendientes

- Versión mínima de Android.
- Confirmar si el usuario necesita conservar exactamente el formato original de las capturas o si el resultado puede guardarse en PNG.
- Definir criterios medibles para marcar una unión como dudosa.
- Seleccionar y fijar las versiones de las dependencias después de validar compatibilidad en ambas plataformas.
