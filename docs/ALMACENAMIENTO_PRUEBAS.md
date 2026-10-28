# Imágenes de prueba privadas en Backblaze B2

El almacenamiento remoto se utiliza solo durante desarrollo y pruebas. La aplicación instalada no se conectará a Backblaze ni a Supabase para procesar imágenes.

## Preparación del bucket

1. En Backblaze B2, usa un bucket privado o crea uno privado dedicado a las pruebas.
2. Crea una carpeta/prefijo `armador-pruebas/`.
3. Sube allí las capturas originales que quieras usar para validar el recorte y el empalme. Conserva nombres claros, por ejemplo `Arizona 1.png` y `Arizona 2.png`.
4. Crea una Application Key limitada al bucket de pruebas, con permisos de lectura. No uses una clave maestra de la cuenta.

## Secrets de GitHub

En el repositorio `SERCO2025/Armador_de_imagenes`, abre Settings → Secrets and variables → Actions → New repository secret. Configura estos nombres, usando los valores de tu cuenta:

- `B2_KEY_ID`: keyID de la Application Key.
- `B2_APPLICATION_KEY`: applicationKey de esa clave.
- `B2_BUCKET`: nombre exacto del bucket.
- `B2_ENDPOINT`: endpoint S3 de la región, por ejemplo `https://s3.us-west-004.backblazeb2.com` (usa el endpoint que indique tu bucket).
- `B2_REGION`: región correspondiente al endpoint, por ejemplo `us-west-004`.

No pegues las claves en el chat, en archivos del repositorio ni en capturas públicas. No uses una clave con permisos de escritura si el proceso solo necesita leer archivos.

## Uso previsto

GitHub Actions descargará las imágenes solo durante las pruebas automatizadas. Los archivos deben permanecer privados y no se publicarán como artefactos de compilación. La integración de descarga se habilitará cuando se confirme la ubicación definitiva de las capturas y se añada el comprobador de empalmes reales.
