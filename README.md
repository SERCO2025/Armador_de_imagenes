# Armador de Imágenes

Aplicación para Windows de 64 bits y Android destinada a recortar automáticamente franjas negras laterales y unir capturas de pantalla verticales en imágenes completas.

## Objetivo funcional

- Procesar una carpeta con muchas capturas en una sola ejecución.
- Identificar parejas mediante nombres como `Arizona 1.png` (parte superior) y `Arizona 2.png` (parte inferior).
- Detectar y recortar las franjas negras de cada imagen por separado, aunque tengan distintos grosores.
- Encontrar la zona de solapamiento y alinear las capturas antes de unirlas.
- Mostrar una vista previa para revisar y corregir uniones dudosas.
- Guardar una imagen final por pareja, sin modificar los originales.
- Informar de parejas incompletas, coincidencias insuficientes y errores.

## Plataformas objetivo

- **Windows 7 de 64 bits**: requisito de compatibilidad prioritario para la versión de escritorio.
- **Android**: aplicación con el mismo flujo de trabajo, adaptado a pantalla táctil.

La compatibilidad real con Windows 7 y las versiones de Android se verificará con compilaciones y pruebas específicas; no se dará por garantizada solo por compartir código.

## Estado

Proyecto recién iniciado. La estructura y los criterios técnicos se documentarán antes de incorporar algoritmos de ensamblado o afirmar que hay una versión funcional.

Consulta [el plan técnico](docs/PLAN_TECNICO.md) para conocer la arquitectura prevista.

## Principios

- Mantener intactos los archivos originales.
- Evitar remuestreo y suavizado innecesarios.
- No recortar contenido útil al detectar márgenes negros.
- No aceptar silenciosamente uniones dudosas.
- Separar la lógica de procesamiento de la interfaz para reutilizarla en ambas plataformas.
