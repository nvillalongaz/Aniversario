# Sorpresa

Página con acceso por contraseña que desbloquea un vídeo y una galería de fotos.

## Archivos que tienes que poner

```
assets/hero.jpg              → la foto de la pantalla de acceso
assets/video/sorpresa.mp4    → el vídeo
assets/fotos/                → las fotos de la galería (.jpg, .png o .webp)
```

Si falta alguno, la app arranca igual: el hero se sustituye por un marcador de
posición y la galería sencillamente no se muestra.

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en http://localhost:8501

## Personalizar

Todo lo editable está en el bloque `CONSTANTES` al principio de `app.py`:
textos, colores, tipografías y rutas.

La contraseña se lee de `.streamlit/secrets.toml`. Al comprobarla se ignoran
mayúsculas, acentos y espacios sobrantes, así que «14 de Junio» y
«14 de junio» valen igual.

## Publicar en Streamlit Community Cloud

1. Sube el proyecto a un repositorio de GitHub (puede ser privado).
   `.gitignore` ya excluye `secrets.toml`.
2. En https://share.streamlit.io crea la app apuntando a `app.py`.
3. En **Settings → Secrets** pega:
   ```toml
   password = "tu contraseña"
   ```

Dos avisos:

- **Esto oculta, no protege.** El vídeo se sirve desde la app y alguien con
  ganas puede llegar a él sin pasar por la contraseña. Sirve para la sorpresa,
  no para guardar nada delicado.
- **Peso del vídeo.** GitHub rechaza archivos de más de 100 MB. Si el tuyo pesa
  más, comprímelo antes (`ffmpeg -i original.mp4 -vcodec libx264 -crf 28
  sorpresa.mp4`) o súbelo a otro sitio y enlázalo con `st.video("URL")`.
