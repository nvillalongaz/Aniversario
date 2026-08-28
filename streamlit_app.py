"""
Acceso con PIN de 4 dígitos que desbloquea un vídeo y una galería.

Para personalizar la app solo necesitas tocar el bloque CONSTANTES.
"""

import base64
import hmac
from pathlib import Path

import streamlit as st

# Paleta clara
COLOR_BG = "#FFFFFF"
COLOR_TEXT = "#111112"
COLOR_MUTED = "#8A8A8E"
COLOR_ACCENT = "#B08D57"
COLOR_KEY = "#F2F2F7"
COLOR_KEY_ACTIVE = "#E3E3E8"

# Tipografía
FONT_SERIF = "'Cormorant Garamond', Georgia, serif"
FONT_SANS = "'Inter', -apple-system, 'Helvetica Neue', Arial, sans-serif"

# Textos
TITLE_TEXT = "Nuestro primer aniversario"
SUBTITLE_TEXT = "Introduce el código"
ERROR_TEXT = "Código incorrecto"
HINT_LABEL = "¿Una pista?"
HINT_TEXT = "🍝​-💪-​🎒-🗻​"
MESSAGE_TEXT = "Esto es para ti."
BACK_TEXT = "Volver"
LOADING_TEXT = "Preparando tu regalo..."

LOADING_SECONDS = 7

DELETE_TEXT = "<"
DELETE_HELP = "Borrar"

# Rutas
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
HERO_IMAGE = ASSETS_DIR / "hero.jpg"
VIDEO_FILE = ASSETS_DIR / "video" / "sorpresa.mp4"
PHOTOS_DIR = ASSETS_DIR / "fotos"

# PIN de 4 dígitos: se lee de .streamlit/secrets.toml
try:
    PIN = str(st.secrets["pin"])
except Exception:
    PIN = "1406"

PIN_LENGTH = 4

# Letras bajo cada tecla, como en el teclado del iPhone
KEY_LETTERS = {
    "2": "ABC",
    "3": "DEF",
    "4": "GHI",
    "5": "JKL",
    "6": "MNO",
    "7": "PQRS",
    "8": "TUV",
    "9": "WXYZ",
}


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────

MIME_BY_SUFFIX = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


@st.cache_data(show_spinner=False)
def data_uri(path_str: str, mtime: float) -> str:
    """Imagen como data URI. `mtime` invalida la caché si reemplazas el archivo."""
    path = Path(path_str)
    mime = MIME_BY_SUFFIX.get(path.suffix.lower(), "image/jpeg")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def image_src(path: Path) -> str:
    if path.exists() and path.is_file() and path.stat().st_size > 0:
        return data_uri(str(path), path.stat().st_mtime)
    return ""


def gallery_images() -> list:
    if not PHOTOS_DIR.exists():
        return []
    return sorted(
        p
        for p in PHOTOS_DIR.iterdir()
        if p.suffix.lower() in MIME_BY_SUFFIX and p.stat().st_size > 0
    )


PLACEHOLDER_SRC = (
    "data:image/svg+xml;utf8,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1600 1000'%3E"
    "%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' "
    "numOctaves='3'/%3E%3C/filter%3E"
    "%3Crect width='1600' height='1000' fill='%23F2F2F7'/%3E"
    "%3Crect width='1600' height='1000' filter='url(%23g)' opacity='0.06'/%3E"
    "%3C/svg%3E"
)


# ─────────────────────────────────────────────────────────────
# LÓGICA DEL PIN
# ─────────────────────────────────────────────────────────────

def press_digit(digit: str) -> None:
    """Añade un dígito y comprueba el código al llegar a 4."""
    if len(st.session_state.pin) >= PIN_LENGTH:
        return

    st.session_state.failed = False
    st.session_state.pin += digit

    if len(st.session_state.pin) == PIN_LENGTH:
        if hmac.compare_digest(st.session_state.pin, PIN):
            st.session_state.unlocked = True
        else:
            st.session_state.failed = True
        st.session_state.pin = ""


def press_delete() -> None:
    st.session_state.pin = st.session_state.pin[:-1]
    st.session_state.failed = False


# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────

KEY_LETTER_CSS = "\n".join(
    f'.st-key-key{d} button::after {{ content: "{letters}"; }}'
    for d, letters in KEY_LETTERS.items()
)

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400&family=Inter:wght@200;300;400&display=swap');

/* ── Ocultar la interfaz nativa de Streamlit ─────────────── */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], [data-testid="stSidebar"],
[data-testid="collapsedControl"], .stDeployButton {{
    display: none !important;
}}
header[data-testid="stHeader"] {{ display: none !important; height: 0 !important; }}

/* ── Fondo claro ─────────────────────────────────────────── */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background-color: {COLOR_BG} !important;
    color: {COLOR_TEXT} !important;
}}

.block-container {{
    max-width: 480px !important;
    padding: 3.5rem 1.5rem 4rem !important;
    margin: 0 auto !important;
}}

.stApp p, .stApp span, .stApp label, .stApp button, .stApp a, .stApp summary {{
    font-family: {FONT_SANS} !important;
    color: {COLOR_TEXT};
}}

/* ── Imagen principal ────────────────────────────────────── */
.hero {{
    width: 100%;
    aspect-ratio: 16 / 10;
    object-fit: cover;
    filter: grayscale(100%) contrast(1.03);
    display: block;
    opacity: 0;
    animation: reveal 800ms ease-out forwards;
}}

/* ── Títulos ─────────────────────────────────────────────── */
.title {{
    font-family: {FONT_SERIF} !important;
    font-size: clamp(1.8rem, 6vw, 2.6rem);
    font-weight: 300;
    text-align: center;
    letter-spacing: 0.04em;
    line-height: 1.15;
    margin: 2.75rem 0 0.6rem;
    opacity: 0;
    animation: reveal 800ms ease-out 200ms forwards;
}}

.subtitle {{
    font-size: 0.76rem;
    font-weight: 300;
    color: {COLOR_MUTED} !important;
    text-align: center;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin: 0 0 2.25rem;
    opacity: 0;
    animation: reveal 800ms ease-out 380ms forwards;
}}

/* ── Puntos del código ───────────────────────────────────── */
.dots {{
    display: flex;
    justify-content: center;
    gap: 22px;
    margin: 0 0 2.5rem;
    opacity: 0;
    animation: reveal 800ms ease-out 480ms forwards;
}}

.dot {{
    width: 13px;
    height: 13px;
    border-radius: 50%;
    border: 1px solid {COLOR_TEXT};
    background: transparent;
    transition: background-color 180ms ease-out, transform 180ms ease-out;
}}

.dot.filled {{
    background: {COLOR_TEXT};
    transform: scale(1.06);
}}

.dots.shake {{
    opacity: 1;
    animation: shake 480ms cubic-bezier(.36,.07,.19,.97);
}}

/* ── Teclado numérico ────────────────────────────────────── */
.st-key-keypad {{
    max-width: 268px;
    margin: 0 auto;
    opacity: 0;
    animation: reveal 800ms ease-out 560ms forwards;
}}

.st-key-keypad [data-testid="stHorizontalBlock"] {{
    gap: 0 !important;
    margin-bottom: 12px !important;
}}

.st-key-keypad [data-testid="stColumn"] {{
    display: flex !important;
    justify-content: center !important;
    padding: 0 !important;
    min-width: 0 !important;
}}

/* Teclas circulares */
.st-key-keypad [data-testid="stButton"] button {{
    width: 74px !important;
    height: 74px !important;
    min-height: 74px !important;
    padding: 0 !important;
    border: none !important;
    border-radius: 50% !important;
    background: {COLOR_KEY} !important;
    color: {COLOR_TEXT} !important;
    box-shadow: none !important;
    position: relative;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: background-color 140ms ease-out, transform 100ms ease-out !important;
}}

.st-key-keypad [data-testid="stButton"] button p {{
    font-family: {FONT_SANS} !important;
    font-size: 1.7rem !important;
    font-weight: 200 !important;
    line-height: 1 !important;
    margin: 0 !important;
    transform: translateY(-5px);
}}

/* Letras bajo el número */
.st-key-keypad [data-testid="stButton"] button::after {{
    position: absolute;
    bottom: 15px;
    left: 0;
    right: 0;
    text-align: center;
    font-family: {FONT_SANS};
    font-size: 0.5rem;
    font-weight: 400;
    letter-spacing: 0.16em;
    color: {COLOR_MUTED};
}}
{KEY_LETTER_CSS}

.st-key-keypad [data-testid="stButton"] button:hover {{
    background: {COLOR_KEY_ACTIVE} !important;
    color: {COLOR_TEXT} !important;
    border: none !important;
}}
.st-key-keypad [data-testid="stButton"] button:active {{
    background: {COLOR_KEY_ACTIVE} !important;
    transform: scale(0.94);
}}
.st-key-keypad [data-testid="stButton"] button:focus-visible {{
    outline: 2px solid {COLOR_ACCENT} !important;
    outline-offset: 3px !important;
}}
.st-key-keypad [data-testid="stButton"] button:focus:not(:focus-visible) {{
    box-shadow: none !important;
}}

/* Tecla de borrado: solo el símbolo, sin círculo de fondo */
.st-key-keydel button,
.st-key-keydel button:hover,
.st-key-keydel button:active,
.st-key-keydel button:disabled {{
    background: transparent !important;
    transform: none !important;
}}

.st-key-keydel button p {{
    font-size: 1.5rem !important;
    font-weight: 200 !important;
    color: {COLOR_MUTED} !important;
    transform: none !important;
    transition: color 140ms ease-out;
}}
.st-key-keydel button:hover p {{ color: {COLOR_TEXT} !important; }}
.st-key-keydel button:active p {{ opacity: 0.5; }}
.st-key-keydel button:disabled {{ opacity: 0 !important; }}

/* ── Mensaje de error ────────────────────────────────────── */
.error {{
    font-size: 0.76rem;
    font-weight: 300;
    color: {COLOR_MUTED} !important;
    text-align: center;
    letter-spacing: 0.06em;
    margin: 1.5rem 0 0;
    animation: reveal 400ms ease-out;
}}

/* ── Pista ───────────────────────────────────────────────── */
.hint {{
    text-align: center;
    margin-top: 2.25rem;
    opacity: 0;
    animation: reveal 800ms ease-out 720ms forwards;
}}
.hint summary {{
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 300;
    color: {COLOR_MUTED} !important;
    letter-spacing: 0.1em;
    cursor: pointer;
    list-style: none;
    transition: color 400ms ease-out;
}}
.hint summary::-webkit-details-marker {{ display: none; }}
.hint summary:hover {{ color: {COLOR_TEXT} !important; }}
.hint p {{
    font-size: 1.5rem;
    font-weight: 300;
    color: {COLOR_MUTED} !important;
    margin: 1rem 0 0;
    animation: reveal 400ms ease-out;
}}

/* ── Pantalla de carga ───────────────────────────────────── */
.loader {{
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: {COLOR_BG};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 26px;
    animation: loaderOut 700ms ease-out {LOADING_SECONDS}s forwards;
}}

.loader-text {{
    font-family: {FONT_SERIF} !important;
    font-size: 1.5rem;
    font-weight: 300;
    color: {COLOR_TEXT};
    letter-spacing: 0.06em;
    animation: loaderPulse 2.4s ease-in-out infinite;
}}

.loader-bar {{
    width: 132px;
    height: 1px;
    background: {COLOR_KEY_ACTIVE};
    overflow: hidden;
}}

.loader-bar span {{
    display: block;
    height: 100%;
    background: {COLOR_ACCENT};
    transform: scaleX(0);
    transform-origin: left;
    animation: loaderFill {LOADING_SECONDS}s cubic-bezier(.4,0,.2,1) forwards;
}}

@keyframes loaderFill {{
    to {{ transform: scaleX(1); }}
}}

@keyframes loaderPulse {{
    0%, 100% {{ opacity: 1; }}
    50%      {{ opacity: 0.45; }}
}}

@keyframes loaderOut {{
    to {{ opacity: 0; visibility: hidden; }}
}}

/* ── Pantalla de contenido ───────────────────────────────── */
.message {{
    font-family: {FONT_SERIF} !important;
    font-size: clamp(1.5rem, 5vw, 2.3rem);
    font-weight: 300;
    text-align: center;
    letter-spacing: 0.03em;
    line-height: 1.35;
    margin: 2.5rem 0 3.5rem;
    opacity: 0;
    animation: reveal 800ms ease-out forwards;
}}

[data-testid="stVideo"] {{
    opacity: 0;
    animation: reveal 800ms ease-out 300ms forwards;
}}
[data-testid="stVideo"] video {{
    width: 100% !important;
    border: none !important;
    border-radius: 0 !important;
    display: block;
}}

.gallery {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 3px;
    margin: 4rem 0 1rem;
    opacity: 0;
    animation: reveal 800ms ease-out 500ms forwards;
}}
.gallery figure {{ margin: 0; aspect-ratio: 1; overflow: hidden; }}
.gallery img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: grayscale(100%);
    transition: filter 800ms ease-out;
}}
.gallery img:hover {{ filter: grayscale(0%); }}
@media (hover: none) {{
    .gallery img {{ filter: grayscale(0%); }}
}}

.note {{
    font-size: 0.78rem;
    font-weight: 300;
    color: {COLOR_MUTED} !important;
    text-align: center;
    margin: 2rem 0;
}}

/* Botón Volver */
.st-key-back {{ display: flex; justify-content: center; margin-top: 2rem; }}
.st-key-back button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: auto !important;
    min-height: 0 !important;
    padding: 0.5rem 1rem !important;
}}
.st-key-back button p {{
    font-size: 0.72rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.24em !important;
    text-transform: uppercase !important;
    color: {COLOR_MUTED} !important;
    margin: 0 !important;
}}
.st-key-back button:hover {{ background: transparent !important; }}
.st-key-back button:hover p {{ color: {COLOR_ACCENT} !important; }}

/* ── Animaciones ─────────────────────────────────────────── */
@keyframes reveal {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: none; }}
}}

@keyframes shake {{
    10%, 90% {{ transform: translateX(-2px); }}
    20%, 80% {{ transform: translateX(4px); }}
    30%, 50%, 70% {{ transform: translateX(-8px); }}
    40%, 60% {{ transform: translateX(8px); }}
}}

@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 1ms !important;
        animation-delay: 0ms !important;
        transition-duration: 1ms !important;
    }}
    .hero, .title, .subtitle, .dots, .hint, .message,
    .gallery, .st-key-keypad, [data-testid="stVideo"] {{
        opacity: 1 !important;
    }}
}}

/* ── Móvil ───────────────────────────────────────────────── */
@media (max-width: 480px) {{
    .block-container {{ padding: 2.25rem 1rem 3rem !important; }}
    .title {{ margin-top: 2rem; }}
    .gallery {{ grid-template-columns: repeat(2, 1fr); gap: 2px; }}
}}
</style>
"""

CSS_WIDE = """
<style>
.block-container { max-width: 840px !important; }
</style>
"""


# ─────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=TITLE_TEXT,
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(CSS, unsafe_allow_html=True)

st.session_state.setdefault("unlocked", False)
st.session_state.setdefault("failed", False)
st.session_state.setdefault("pin", "")
st.session_state.setdefault("intro_done", False)


# ─────────────────────────────────────────────────────────────
# PANTALLA 1 — ACCESO
# ─────────────────────────────────────────────────────────────

def render_dots() -> None:
    """Los cuatro puntos, rellenos según los dígitos introducidos."""
    n = len(st.session_state.pin)
    puntos = "".join(
        f'<span class="dot{" filled" if i < n else ""}"></span>'
        for i in range(PIN_LENGTH)
    )
    clase = "dots shake" if st.session_state.failed else "dots"
    st.markdown(f'<div class="{clase}">{puntos}</div>', unsafe_allow_html=True)


def render_keypad() -> None:
    """Teclado 3x4: 1-9, hueco, 0 y Borrar."""
    filas = [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"], ["", "0", "del"]]

    with st.container(key="keypad"):
        for fila in filas:
            cols = st.columns(3, gap="small")
            for col, tecla in zip(cols, fila):
                with col:
                    if tecla == "":
                        st.markdown("&nbsp;", unsafe_allow_html=True)
                    elif tecla == "del":
                        st.button(
                            DELETE_TEXT,
                            key="keydel",
                            help=DELETE_HELP,
                            on_click=press_delete,
                            disabled=not st.session_state.pin,
                        )
                    else:
                        st.button(
                            tecla,
                            key=f"key{tecla}",
                            on_click=press_digit,
                            args=(tecla,),
                        )


def render_access() -> None:
    hero = image_src(HERO_IMAGE) or PLACEHOLDER_SRC
    st.markdown(f'<img class="hero" src="{hero}" alt="">', unsafe_allow_html=True)

    st.markdown(f'<h1 class="title">{TITLE_TEXT}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="subtitle">{SUBTITLE_TEXT}</p>', unsafe_allow_html=True)

    render_dots()
    render_keypad()

    if st.session_state.failed:
        st.markdown(f'<p class="error">{ERROR_TEXT}</p>', unsafe_allow_html=True)

    st.markdown(
        f'<details class="hint"><summary>{HINT_LABEL}</summary>'
        f"<p>{HINT_TEXT}</p></details>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────
# PANTALLA 2 — CONTENIDO
# ─────────────────────────────────────────────────────────────

def render_loader() -> None:
    """Cortina que cubre la página mientras se decodifican fotos y vídeo.

    Se desvanece sola por CSS. Solo aparece la primera vez que se desbloquea,
    para que no se repita en cada recarga interna de Streamlit.
    """
    if st.session_state.intro_done:
        return
    st.session_state.intro_done = True
    st.markdown(
        f'<div class="loader">'
        f'<span class="loader-text">{LOADING_TEXT}</span>'
        f'<span class="loader-bar"><span></span></span>'
        f"</div>",
        unsafe_allow_html=True,
    )


def render_content() -> None:
    render_loader()
    st.markdown(CSS_WIDE, unsafe_allow_html=True)
    st.markdown(f'<p class="message">{MESSAGE_TEXT}</p>', unsafe_allow_html=True)

    if VIDEO_FILE.exists() and VIDEO_FILE.stat().st_size > 0:
        st.video(str(VIDEO_FILE))
    else:
        st.markdown(
            '<p class="note">Coloca el vídeo en assets/video/sorpresa.mp4</p>',
            unsafe_allow_html=True,
        )

    fotos = gallery_images()
    if fotos:
        celdas = "".join(
            f'<figure><img src="{image_src(p)}" alt=""></figure>' for p in fotos
        )
        st.markdown(f'<div class="gallery">{celdas}</div>', unsafe_allow_html=True)

    if st.button(BACK_TEXT, key="back"):
        st.session_state.unlocked = False
        st.session_state.failed = False
        st.session_state.pin = ""
        st.session_state.intro_done = False
        st.rerun()


# ─────────────────────────────────────────────────────────────
# ENRUTADO
# ─────────────────────────────────────────────────────────────

if st.session_state.unlocked:
    render_content()
else:
    render_access()