# Plan técnico — Armador de Imágenes

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

## 6. Procesamiento por lotes y seguridad

- Leer los originales sin modificarlos.
- Escribir resultados en una carpeta de salida separada.
- Producir un informe con archivos procesados, pendientes y errores.
- Permitir repetir el proceso sin sobrescribir originales.
- Controlar el uso de memoria para carpetas grandes.

## 7. Compatibilidad de plataformas

### Windows 7 de 64 bits

La compatibilidad con Windows 7 condiciona la selección de Python, Kivy y bibliotecas binarias. Se debe fijar una combinación de versiones compatible y probarla en Windows 7 real o en una máquina virtual antes de elegirla como versión de producción. No actualizar dependencias a ciegas si eso rompe el soporte de Windows 7.

### Android

El empaquetado Android requiere verificar que las dependencias del núcleo puedan compilarse e instalarse con la cadena de herramientas Android elegida. La selección de archivos debe funcionar con los mecanismos de almacenamiento disponibles en las versiones de Android que se decidan soportar.

## 8. Fases propuestas

1. Crear pruebas del emparejamiento por nombres.
2. Implementar y probar detección de franjas negras con anchos variables.
3. Implementar búsqueda de solapamiento y unión vertical.
4. Crear un conjunto de pruebas con capturas sintéticas y reales.
5. Añadir la interfaz de revisión y corrección manual.
6. Añadir procesamiento por lotes e informe.
7. Empaquetar y probar Windows 7 de 64 bits.
8. Empaquetar y probar Android.

## 9. Decisiones pendientes

- Versión mínima de Android.
- Confirmar si el usuario necesita conservar exactamente el formato original de las capturas o si el resultado puede guardarse en PNG.
- Definir criterios medibles para marcar una unión como dudosa.
- Seleccionar y fijar las versiones de las dependencias después de validar compatibilidad en ambas plataformas.
