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
p4a.branch = v2024.01.21
requirements = python3,kivy==2.1.0,pillow==9.5.0,numpy==1.22.3
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
