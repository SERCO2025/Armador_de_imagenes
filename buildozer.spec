[app]

title = Armador de Imágenes
package.name = armadordeimagenes
package.domain = mx.serco2025
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
# Incluir explícitamente el motor local; main.py añade src al sys.path.
source.include_patterns = src/armador/*.py
source.exclude_dirs = .git,.github,.buildozer,bin,build,dist,tests,docs,__pycache__
version = 0.1.0
# Commit fijado con recetas compatibles con Python 3.11: Kivy 2.3.0,
# NumPy 1.26.5 y Pillow 10.3.0.
p4a.branch = v2024.01.21
# Dejar que python-for-android seleccione las versiones de sus recetas compatibles
# con el Python que realmente construye para Android (3.11 en la compilación 15).
requirements = python3,kivy,pillow,numpy
orientation = portrait
fullscreen = 0

android.permissions =
android.api = 31
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1
