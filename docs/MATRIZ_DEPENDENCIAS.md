# Matriz inicial de dependencias

Estado: **selección preliminar; todavía no es un entorno validado ni un archivo de dependencias de producción**.

El objetivo de esta matriz es reducir riesgos antes de programar el núcleo. Las versiones propuestas deben probarse con instalaciones limpias y con los paquetes binarios exactos. No actualizar versiones automáticamente.

## Decisiones y candidatos

| Componente | Versión candidata | Uso | Estado / advertencias |
|---|---|---|---|
| Python para Windows | 3.7.9 x64 | Entorno principal acordado para Windows 7 | Versión solicitada por el usuario. Python 3.7 está fuera de soporte de seguridad; fijar y aislar el entorno. |
| Pillow | 9.5.0 | Abrir, recortar, componer y guardar imágenes; escribir metadatos de resolución | Candidato compatible con Python 3.7 y con wheel de Windows x64. Probar en Windows 7 real/VM. |
| NumPy | 1.21.6 | Comparación de píxeles y cálculo de coincidencias | Candidato con wheel CPython 3.7 x64. En Android depende de la receta y toolchain fijadas. |
| Kivy | 2.1.0 | Interfaz compartida candidata para Windows y Android | Publica wheels para CPython 3.7 y documenta soporte de Python 3.7–3.10. Compatibilidad gráfica en Windows 7 y empaquetado Android aún deben probarse. |
| PyInstaller | 5.13.2 | Empaquetar la aplicación de escritorio en EXE | Declara Python 3.7–3.12 y que debería funcionar desde Windows 7, aunque su soporte oficial es Windows 8 o posterior. Validar en Windows 7. |
| OpenCV | No se añade todavía | Posible ayuda para detectar y verificar solapamientos | Evitar añadirlo antes de demostrar que Pillow + NumPy no bastan. Sus wheels, tamaño, dependencias del sistema y receta Android requieren validación aparte. |
| Motor de superresolución por IA | No se añade todavía | Variante opcional de ampliación | Se evaluará después del núcleo. Debe trabajar localmente, incluir el modelo y tener licencia compatible. La fidelidad de texto debe compararse contra el original. |

## Fuentes oficiales consultadas

- [Python 3.7.9 — aviso de fin de soporte](https://www.python.org/downloads/release/python-379/)
- [Pillow 9.5.0 en PyPI](https://pypi.org/project/Pillow/9.5.0/)
- [NumPy 1.21.6 en PyPI](https://pypi.org/project/numpy/1.21.6/)
- [Kivy 2.1.0 — instalación y versiones de Python](https://kivy.org/doc/stable-2.1.0/gettingstarted/installation.html)
- [PyInstaller 5.13.2 en PyPI](https://pypi.org/project/pyinstaller/5.13.2/)
- [python-for-android — documentación y recetas](https://python-for-android.readthedocs.io/)

## Riesgo importante: Android

La versión de Python del desarrollo de escritorio no demuestra por sí sola que una APK se pueda compilar con el mismo conjunto de herramientas. El proyecto Android debe fijar una versión concreta de Buildozer/python-for-android, SDK, NDK y API mínima que pueda compilar el intérprete y las dependencias necesarias.

No se debe actualizar la cadena Android a la versión más reciente sin comprobar si conserva la posibilidad de usar Python 3.7.9. Si no se consigue una combinación reproducible, hay que documentar la incompatibilidad antes de elegir una solución alternativa; no afirmar que ambas plataformas comparten exactamente el mismo entorno sin una compilación real.

## Política de dependencias y modo sin conexión

- Mantener versiones fijadas en archivos de configuración una vez validadas.
- Registrar las licencias de las dependencias y los modelos distribuidos.
- Distribuir todos los componentes necesarios en el instalador/paquete final.
- No descargar modelos, bibliotecas ni recursos al iniciar o utilizar la aplicación.
- Probar las funciones con Wi-Fi y datos móviles desactivados.
- Mantener el motor de imágenes separado de la interfaz para compartir las pruebas de procesamiento.
- No añadir OpenCV ni IA al núcleo hasta justificar su necesidad con pruebas.

## Siguiente verificación

1. Preparar un entorno limpio con Python 3.7.9 x64 y comprobar la instalación/importación de Pillow 9.5.0, NumPy 1.21.6 y Kivy 2.1.0.
2. Ejecutar una prueba mínima de apertura, recorte, composición y guardado PNG/JPEG con metadatos de 300 ppp.
3. Probar el empaquetado EXE en Windows 7 real o máquina virtual, incluyendo los runtimes del sistema necesarios.
4. Probar por separado la cadena Android antes de declarar elegida la versión de Buildozer/python-for-android.
5. Solo después convertir estos candidatos en requisitos definitivos y comenzar el núcleo completo.
