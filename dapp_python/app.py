import streamlit as st
import time
import pandas as pd
from web3 import Web3
from web3_utils import Web3Manager
from db import init_db, save_tx, get_history
import os
from dotenv import load_dotenv
from logger_config import get_logger, LOG_PATH

# Logger de la capa de interfaz.
# Usamos 'app' como nombre para distinguirlo de 'db' o 'web3_utils' en el log.
logger = get_logger(__name__)

# Carga variables del archivo .env (si existe) para no escribir secretos en el código.
load_dotenv()

# Inicializa la base de datos SQLite local (crea la tabla si aún no existe).
# init_db() es idempotente: si la tabla ya existe, no hace nada.
init_db()
logger.info("Aplicación TSender iniciada")

# Configuración general de la página de Streamlit (título, icono y ancho del layout).
st.set_page_config(page_title="TSender", page_icon="🚀", layout="wide")

# --- Custom CSS for the aesthetic ---
# Este bloque solo cambia el estilo visual (colores, bordes, tipografías, etc.).
# No realiza ninguna operación de blockchain ni modifica datos.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --bg-0: #0b0f1a;
        --bg-1: #0b0f1a;
        --panel: rgba(11, 15, 26, 0.88);
        --panel-2: rgba(11, 15, 26, 0.8);
        --card: rgba(11, 15, 26, 0.86);
        --border: rgba(34, 211, 238, 0.25);
        --text: #e5e7eb;
        --muted: #9ca3af;
        --brand-1: #0ea5e9;
        --brand-2: #22d3ee;
        --accent: #22d3ee;
        --success: #34d399;
    }

    * { transition: all 0.2s ease; }

    .stApp {
        background:
            radial-gradient(900px 380px at 50% -8%, rgba(14, 165, 233, 0.16), transparent 62%),
            linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 100%);
        color: var(--text);
        font-family: 'Manrope', sans-serif;
    }

    .block-container {
        max-width: 100%;
        padding-top: 1.8rem;
        padding-bottom: 2.4rem;
    }

    section.main > div {
        max-width: 100%;
        width: 100%;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(11, 15, 26, 0.88), rgba(11, 15, 26, 0.84));
        border-right: 1px solid rgba(34, 211, 238, 0.08);
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label { color: var(--text) !important; }
    section[data-testid="stSidebar"] h2 { color: var(--text) !important; }

    .header-container {
        position: relative;
        overflow: hidden;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1.4rem;
        padding: 0.9rem 1.4rem;
        border: 1px solid var(--border);
        background: linear-gradient(180deg, rgba(11, 15, 26, 0.72), rgba(11, 15, 26, 0.56));
        border-radius: 18px;
        margin: 0.55rem auto 1.75rem auto;
        box-shadow:
            0 24px 48px rgba(2, 8, 23, 0.34),
            0 0 0 1px rgba(34, 211, 238, 0.08),
            0 0 18px rgba(34, 211, 238, 0.14);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }
    .header-container::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0.55;
        background: radial-gradient(700px 120px at 50% 0%, rgba(34, 211, 238, 0.16), transparent 70%);
    }
    .header-container:hover {
        border-color: rgba(34, 211, 238, 0.35);
        transform: translateY(-1px);
        box-shadow:
            0 26px 52px rgba(2, 8, 23, 0.36),
            0 0 0 1px rgba(34, 211, 238, 0.16),
            0 0 26px rgba(34, 211, 238, 0.25);
    }
    .header-container:hover::before { opacity: 0.9; }

    .header-left, .header-center, .header-right { display: flex; align-items: center; }
    .header-center { flex: 1; justify-content: center; }
    .header-right { justify-content: flex-end; }

    .brand-wrap { display: flex; align-items: center; gap: 0.7rem; }
    .brand-mark {
        width: 38px; height: 38px; border-radius: 999px;
        position: relative; overflow: hidden; isolation: isolate;
        background: linear-gradient(135deg, #0ea5e9, #22d3ee);
        display: flex; align-items: center; justify-content: center;
        gap: 0.5px; color: white; font-size: 0.82rem; font-weight: 800;
        letter-spacing: -0.25px; line-height: 1;
        box-shadow: 0 10px 20px rgba(34,211,238,0.24), 0 0 0 1px rgba(34,211,238,0.32), 0 0 14px rgba(34,211,238,0.2);
    }
    .brand-mark::before {
        content: ""; position: absolute; inset: 2px; border-radius: 999px;
        background: linear-gradient(180deg, rgba(11,15,26,0.98), rgba(11,15,26,0.8)); z-index: 1;
    }
    .logo-t { color:#fff; display:inline-block; position:relative; z-index:2; }
    .logo-s { color:#fff; display:inline-block; position:relative; z-index:2; opacity:0.95; }
    .logo-text { font-size:1.2rem; font-weight:800; letter-spacing:0.48px; color:var(--text); text-transform:uppercase; }

    .nav-links { display:flex; gap:0.6rem; font-size:0.74rem; color:var(--text); font-weight:600; text-transform:uppercase; letter-spacing:0.88px; }
    .nav-pill {
        padding: 0.46rem 0.82rem; border-radius: 999px;
        border: 1px solid rgba(34,211,238,0.2);
        background: rgba(11,15,26,0.55); color: var(--text);
    }
    .nav-pill:hover {
        border-color: rgba(34,211,238,0.34);
        box-shadow: 0 0 0 1px rgba(34,211,238,0.2), 0 0 12px rgba(34,211,238,0.18);
        filter: brightness(1.04);
    }

    .nav-pill:hover {
        border-color: rgba(34, 211, 238, 0.34);
        box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.2), 0 0 12px rgba(34, 211, 238, 0.18);
        filter: brightness(1.04);
    }

    .connect-btn {
        display: inline-flex; align-items: center; gap: 0.5rem;
        background: linear-gradient(135deg, rgba(14,165,233,0.24), rgba(34,211,238,0.18));
        border: 1px solid rgba(34,211,238,0.34); color: var(--text);
        padding: 0.54rem 0.9rem; border-radius: 999px;
        font-weight: 700; font-size: 0.76rem; letter-spacing: 0.56px; text-transform: uppercase;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.12);
    }
    .wallet-dot {
        width: 8px; height: 8px; border-radius: 999px; background: #22d3ee;
        box-shadow: 0 0 0 4px rgba(34,211,238,0.2), 0 0 10px rgba(34,211,238,0.25);
    }

    .hero-wrap { position: relative; margin-bottom: 1.35rem; }
    .hero-wrap::before {
        content: ""; position: absolute; width: 76%; height: 170px; left: 12%; top: -28px;
        background: radial-gradient(closest-side, rgba(34,211,238,0.25), transparent 72%);
        filter: blur(10px); pointer-events: none;
    }

    .main-card {
        --x: 50%; --y: 50%;
        position: relative;
        background: linear-gradient(145deg, var(--card) 0%, var(--panel-2) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(34,211,238,0.28);
        border-radius: 18px; padding: 3.2rem 2.2rem;
        text-align: center; margin-bottom: 0; margin-top: 1rem;
        overflow: hidden;
        box-shadow: 0 28px 56px rgba(2,8,23,0.42);
    }
    .main-card::before {
        content: ""; position: absolute; inset: 0; opacity: 0;
        background: radial-gradient(260px 220px at var(--x) var(--y), rgba(34,211,238,0.25), rgba(34,211,238,0.12) 38%, rgba(0,0,0,0) 70%);
        pointer-events: none; z-index: 1;
        transition: opacity 0.15s ease;
    }
    .main-card::after {
        content: ""; position: absolute; inset: 0;
        background:
            radial-gradient(500px 230px at 10% -20%, rgba(14,165,233,0.12), transparent 60%),
            radial-gradient(440px 230px at 92% 118%, rgba(34,211,238,0.1), transparent 60%);
        pointer-events: none; z-index: 0;
    }
    .main-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(34,211,238,0.45);
        box-shadow: 0 34px 66px rgba(2,8,23,0.5), 0 0 26px rgba(34,211,238,0.25);
    }
    .main-card:hover::before { opacity: 1; }

    .gradient-text {
        position: relative; z-index: 2;
        font-size: 3rem; font-weight: 800; line-height: 1.12; letter-spacing: -0.55px;
        background: linear-gradient(90deg, #e5e7eb 0%, #22d3ee 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.85rem;
    }
    .subtitle { position:relative; z-index:2; color:var(--text); font-size:1.08rem; max-width:700px; margin:0 auto; line-height:1.55; }
    .ui-kicker { position:relative; z-index:2; color:var(--accent); font-size:0.74rem; text-transform:uppercase; letter-spacing:1.6px; font-weight:700; margin-bottom:0.5rem; }

    .section-title { font-size:1.15rem; color:var(--text); font-weight:700; letter-spacing:0.25px; margin:0.25rem 0 0.35rem 0; }
    .section-helper { color:var(--muted); font-size:0.93rem; margin-bottom:0.9rem; line-height:1.45; }

    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {
        position: relative;
        background: rgba(16, 24, 36, 0.82) !important;
        border: 2.2px solid rgba(45, 212, 191, 0.42) !important;
        border-radius: 16px !important;
        padding: 0.6rem !important;
        margin: 0 0 1rem 0;
        box-shadow:
            0 14px 28px rgba(2, 8, 23, 0.38),
            0 0 18px rgba(45, 212, 191, 0.18),
            inset 0 0 0 1px rgba(45, 212, 191, 0.1) !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        overflow: hidden;
        transition: border-color 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;
    }
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]::before {
        content: ""; position: absolute; inset: 0; pointer-events: none;
        background:
            radial-gradient(560px 120px at 10% -10%, rgba(45, 212, 191, 0.16), transparent 65%),
            radial-gradient(420px 190px at 95% 110%, rgba(45, 212, 191, 0.08), transparent 68%);
        opacity: 0.86;
    }
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:hover {
        transform: translateY(-2px);
        border-color: rgba(45, 212, 191, 0.65) !important;
        box-shadow:
            0 18px 34px rgba(2, 8, 23, 0.42),
            0 0 28px rgba(45, 212, 191, 0.24),
            inset 0 0 0 1px rgba(45, 212, 191, 0.18) !important;
    }
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:hover::before { opacity: 1; }
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] h4 { font-size:1.28rem !important; font-weight:800 !important; margin-bottom:0.2rem !important; }

    /* Igualar altura de cards dentro de columnas */
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        display: flex;
        flex-direction: column;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stLayoutWrapper"] {
        display: flex;
        flex: 1 1 auto;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"] {
        height: 100%;
        flex: 1 1 auto;
    }

    /* Centrado completo para cards de métricas */
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has([data-testid="stMetric"]) {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
    }
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has([data-testid="stMetric"]) > div[data-testid="stElementContainer"] {
        width: 100%;
        display: flex;
        justify-content: center;
    }
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetric"] {
        align-items: center;
        text-align: center;
    }
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetricLabel"],
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has([data-testid="stMetric"]) [data-testid="stMetricValue"],
    div[data-testid="stLayoutWrapper"] > div[data-testid="stVerticalBlock"]:has([data-testid="stMetric"]) [data-testid="stMarkdownContainer"] p {
        text-align: center !important;
        justify-content: center;
        width: 100%;
    }

    h3 { color: var(--text) !important; font-size: 1.62rem !important; }
    h4 { color: var(--text) !important; font-size: 1.24rem !important; }

    [data-baseweb="tab-list"] {
        justify-content: center; width: fit-content;
        margin: 0.5rem auto 1.15rem auto;
        gap: 0.6rem;
        background: rgba(11,15,26,0.7);
        border: 1px solid var(--border); border-radius: 14px;
        padding: 0.42rem;
        box-shadow: 0 14px 32px rgba(2,8,23,0.32);
    }
    [data-baseweb="tab"] {
        position: relative;
        background: rgba(11,15,26,0.55) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        font-weight: 700 !important;
        border: 1px solid rgba(34,211,238,0.18) !important;
        padding: 0.58rem 1rem !important;
        min-width: 155px; text-align: center;
    }
    [data-baseweb="tab-highlight"] { background-color: transparent !important; box-shadow: none !important; opacity: 0 !important; }
    [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(14,165,233,0.3), rgba(34,211,238,0.22)) !important;
        color: var(--text) !important;
        border-color: rgba(34,211,238,0.46) !important;
        box-shadow: 0 10px 22px rgba(34,211,238,0.25);
    }
    [data-baseweb="tab"][aria-selected="true"]::after {
        content: ""; position: absolute; left:14px; right:14px; bottom:6px;
        height: 2px; border-radius: 999px;
        background: linear-gradient(90deg, rgba(34,211,238,0.6), rgba(34,211,238,1));
        box-shadow: 0 0 12px rgba(34,211,238,0.35);
    }
    [data-baseweb="tab"]:hover { filter: brightness(1.06); }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
        background: linear-gradient(180deg, rgba(11,15,26,0.95), rgba(11,15,26,0.84)) !important;
        color: var(--text) !important;
        border: 1px solid rgba(34,211,238,0.25) !important;
        border-radius: 10px !important;
        min-height: 2.85rem;
        padding-left: 0.8rem !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(34,211,238,0.66) !important;
        box-shadow: 0 0 0 2px rgba(34,211,238,0.25) !important;
        outline: none !important;
    }
    [data-testid="stNumberInput"] input:hover,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stNumberInput"] input:focus-visible,
    [data-testid="stNumberInput"] input:active,
    [data-testid="stNumberInput"] input:invalid {
        border-color: rgba(34,211,238,0.66) !important;
        box-shadow: 0 0 0 2px rgba(34,211,238,0.22) !important;
        outline: none !important;
    }
    [data-testid="stTextArea"] textarea { min-height: 112px !important; }

    [data-baseweb="input"] {
        background: rgba(11,15,26,0.9) !important;
        border: 1px solid rgba(34,211,238,0.25) !important;
        border-radius: 10px !important;
    }
    [data-baseweb="base-input"] {
        background: rgba(11,15,26,0.9) !important;
        border: 1px solid rgba(34,211,238,0.25) !important;
        border-radius: 10px !important;
    }
    [data-baseweb="input"]:focus-within {
        border-color: rgba(34,211,238,0.66) !important;
        box-shadow: 0 0 0 2px rgba(34,211,238,0.2) !important;
    }
    [data-baseweb="base-input"]:focus-within {
        border-color: rgba(34,211,238,0.66) !important;
        box-shadow: 0 0 0 2px rgba(34,211,238,0.2) !important;
    }
    [data-testid="stNumberInput"] [data-baseweb="input"]:has(input:invalid),
    [data-testid="stNumberInput"] [data-baseweb="base-input"]:has(input:invalid) {
        border-color: rgba(34,211,238,0.66) !important;
        box-shadow: 0 0 0 2px rgba(34,211,238,0.2) !important;
    }
    [data-testid="stNumberInput"] [data-baseweb="input"]:hover,
    [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within {
        border-color: rgba(34,211,238,0.66) !important;
        box-shadow: 0 0 0 2px rgba(34,211,238,0.2) !important;
    }
    [data-testid="stNumberInput"] [data-baseweb="base-input"]:hover,
    [data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
        border-color: rgba(34,211,238,0.66) !important;
        box-shadow: 0 0 0 2px rgba(34,211,238,0.2) !important;
    }
    [data-testid="stNumberInput"] button {
        background: rgba(11,15,26,0.92) !important;
        color: var(--text) !important;
        border-left: 1px solid rgba(34,211,238,0.3) !important;
    }
    [data-testid="stNumberInput"] button:hover {
        background: rgba(34,211,238,0.14) !important;
        color: var(--text) !important;
    }

    [data-testid="stButton"] button {
        background: rgba(34,211,238,0.12);
        color: var(--text); font-weight: 800;
        border: 1px solid rgba(34,211,238,0.28);
        width: 100%; padding: 0.8rem 1.1rem;
        border-radius: 10px;
        margin-top: 0.95rem;
        box-shadow: 0 8px 16px rgba(34,211,238,0.1);
        letter-spacing: 0.2px;
        transition: all 0.25s ease;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    [data-testid="stButton"] button:hover {
        background: rgba(34,211,238,0.18);
        border-color: rgba(34,211,238,0.45);
        box-shadow: 0 10px 24px rgba(34,211,238,0.18);
        color: var(--text);
    }
    [data-testid="stButton"] button:active {
        background: rgba(34,211,238,0.14);
        box-shadow: 0 6px 12px rgba(34,211,238,0.12);
    }

    [data-testid="stTextInput"] label,
    [data-testid="stTextArea"] label,
    [data-testid="stNumberInput"] label {
        color: var(--text) !important; font-size: 0.92rem !important; font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] { color: var(--success); }
    [data-testid="stMetricLabel"] { color: var(--muted); }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(34,211,238,0.24) !important;
        background: linear-gradient(160deg, rgba(11,15,26,0.92), rgba(11,15,26,0.78)) !important;
        color: var(--text) !important;
        box-shadow: 0 8px 18px rgba(2,8,23,0.28);
    }
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p { color: var(--text) !important; }

    .stCodeBlock, .stCode { border-radius: 10px; border: 1px solid rgba(34,211,238,0.22); }

    hr { display: none !important; }

    .stSuccess { border-color: rgba(52,211,153,0.45) !important; }
    .stSuccess [data-testid="stMarkdownContainer"] { color: var(--success) !important; }

    @media (max-width: 900px) {
        .header-container { padding: 0.9rem; flex-direction: column; align-items: flex-start; gap: 0.75rem; }
        .header-center, .header-right { width: 100%; justify-content: flex-start; }
        .nav-links { flex-wrap: wrap; }
        [data-baseweb="tab"] { min-width: 112px; }
        .gradient-text { font-size: 2.08rem; }
        .subtitle { font-size: 0.98rem; }
    }
</style>
""", unsafe_allow_html=True)


# --- Siderbar: Configuración Web3 ---
# Sidebar: aquí el usuario configura conexión y credenciales.
with st.sidebar:
    st.header("Configuración Web3")
    st.info("Dado que esto es Python puro vamos a inyectar la URL del nodo (RPC) y la Private Key directamente.")

    # Input 1: URL RPC del nodo al que nos conectamos (por defecto Sepolia).
    rpc_url = st.text_input("RPC URL", value=os.getenv("RPC_URL", "https://rpc.sepolia.org"))
    # Input 2: clave privada para firmar transacciones desde la billetera.
    private_key = st.text_input("Private Key", type="password", value=os.getenv("PRIVATE_KEY", ""))

    # Punto de unión frontend-backend: crea el gestor Web3 con los datos del usuario.
    w3_manager = Web3Manager(rpc_url, private_key)

    # Estado de conexión: consulta al backend si el nodo responde.
    if w3_manager.is_connected():
        st.success("🟢 Conectado al nodo Blockchain")
        # Si hay clave válida, se muestra dirección y balance consultando el backend.
        if w3_manager.get_address():
            st.write(f"**Billetera:**")
            st.code(w3_manager.get_address())
            st.write(f"**Balance:** {float(w3_manager.get_balance()):.4f} ETH")
        else:
            st.info("ℹ️ Introduce tu Private Key.")
    else:
        st.error("🔴 No conectado.")

# --- Header ---
# Header superior: muestra resumen de la wallet para dar contexto al usuario.
wallet_text = f"{w3_manager.get_address()[:6]}...{w3_manager.get_address()[-4:]}" if w3_manager.get_address() else "Esperando billetera..."

# Se renderiza HTML simple para logo, navegación visual y estado de conexión.
st.markdown(f"""
<div class="header-container">
    <div class="header-left">
        <div class="brand-wrap">
            <span class="brand-mark"><span class="logo-t">T</span><span class="logo-s">S</span></span>
            <span class="logo-text">TSender</span>
        </div>
    </div>
    <div class="header-center">
        <div class="nav-links">
            <span class="nav-pill">Dashboard</span>
            <span class="nav-pill">Airdrop</span>
            <span class="nav-pill">Deploy</span>
        </div>
    </div>
    <div class="header-right">
        <div class="connect-btn"><span class="wallet-dot"></span>{wallet_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Main container ---
# Tarjeta de bienvenida con efecto spotlight al mover el ratón.
st.markdown("""
<div class="hero-wrap">
<div class="main-card" onmousemove="const r=this.getBoundingClientRect(); this.style.setProperty('--x', ((event.clientX-r.left)/r.width*100)+'%'); this.style.setProperty('--y', ((event.clientY-r.top)/r.height*100)+'%');" onmouseleave="this.style.setProperty('--x','50%'); this.style.setProperty('--y','50%');">
    <div class="ui-kicker">TSender Web3 Console</div>
    <div class="gradient-text">Gestiona tus envíos on-chain con TSender</div>
    <div class="subtitle">Conecta tu wallet, despliega contratos y ejecuta airdrops desde una interfaz limpia, coherente y profesional.</div>
</div>
</div>
""", unsafe_allow_html=True)

# --- Tabs Navigation ---
# Tabs: separan funcionalidades para que el estudiante entienda el flujo por módulos.
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Dashboard", "Airdrop", "Deploy", "Historial", "Logs", "Estadísticas"])

with tab1:
    # TAB 1: panel de estado, donaciones y lectura de donantes.
    st.markdown("<div class='section-title'>Resumen de Cuenta</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-helper'>Consulta tu wallet, revisa contratos y gestiona donaciones desde un único panel.</div>", unsafe_allow_html=True)
    st.markdown("### Tu balance y estado")
    # Si no hay wallet, se bloquean acciones que requieren firma de transacción.
    if w3_manager.get_address():
        # Fila superior: tres métricas clave (wallet, balance y balance de contrato).
        with st.container(border=True):
            st.markdown("#### Balance")
            st.caption("Estado de tu wallet y consulta rápida de contratos.")
            col_metric_1, col_metric_2, col_metric_3 = st.columns(3)

            with col_metric_1:
                with st.container(border=True):
                    wallet_addr = w3_manager.get_address()
                    st.caption("Wallet")
                    st.metric(" ", f"{wallet_addr[:6]}...{wallet_addr[-4:]}")
                    st.caption(wallet_addr)

            with col_metric_2:
                with st.container(border=True):
                    st.caption("Balance")
                    st.metric(" ", f"{float(w3_manager.get_balance()):.4f} ETH")

            with col_metric_3:
                with st.container(border=True):
                    st.caption("Contract Balance")
                    contract_to_check = st.text_input("Contrato para consulta", placeholder="0x...", key="check_balance")
                    if contract_to_check:
                        try:
                            # Llamada backend: get_contract_eth_balance() solo lee estado en cadena.
                            c_balance = w3_manager.get_contract_eth_balance(contract_to_check)
                            st.metric(" ", f"{float(c_balance):.4f} ETH")
                        except Exception:
                            st.metric(" ", "-")
                            st.error("Dirección no válida")
                    else:
                        st.metric(" ", "-")

        # Fila inferior: izquierda donaciones, derecha lista de donantes.
        col_left, col_right = st.columns(2)

        with col_left:
            with st.container(border=True, height=500):
                st.markdown("#### Donaciones")
                st.caption("Introduce contrato y monto. Al confirmar, se firma y envía una transacción en blockchain.")
                st.markdown("##### Realizar donación al contrato")

                if "donation_feedback_kind" not in st.session_state:
                    st.session_state["donation_feedback_kind"] = "caption"
                    st.session_state["donation_feedback_text"] = "El estado de la donación aparecerá aquí."

                target_contract = st.text_input("Dirección Contrato Destino", placeholder="0x...", key="donate_addr")
                donation_amount = st.number_input("Cantidad a donar (ETH)", min_value=0.0001, format="%.4f")
                donation_feedback_kind = st.session_state["donation_feedback_kind"]
                donation_feedback_text = st.session_state["donation_feedback_text"]
                if donation_feedback_kind == "success":
                    st.success(donation_feedback_text)
                elif donation_feedback_kind == "warning":
                    st.warning(donation_feedback_text)
                elif donation_feedback_kind == "error":
                    st.error(donation_feedback_text)
                else:
                    st.caption(donation_feedback_text)
                # Al pulsar este botón se firma y envía una transacción real de ETH.
                donate_clicked = st.button("Donar ahora", use_container_width=True)
                if donate_clicked:
                    if target_contract:
                        try:
                            with st.spinner("Procesando donación..."):
                                # Llamada backend: donate_eth() construye, firma y envía la transacción.
                                tx = w3_manager.donate_eth(target_contract, donation_amount)
                            # Persistimos la donación en SQLite para el historial
                            save_tx("Donación", tx, desde=w3_manager.get_address(), contrato=target_contract)
                            st.session_state["donation_feedback_kind"] = "success"
                            st.session_state["donation_feedback_text"] = f"¡Donación exitosa! TX: {tx[:10]}..."
                            st.balloons()
                        except Exception as e:
                            logger.error("Error en donación a %s: %s", target_contract, e)
                            st.session_state["donation_feedback_kind"] = "error"
                            st.session_state["donation_feedback_text"] = f"Error: {e}"
                    else:
                        logger.warning("Intento de donación sin dirección de contrato")
                        st.session_state["donation_feedback_kind"] = "warning"
                        st.session_state["donation_feedback_text"] = "Pon la dirección del contrato."
                    st.rerun()

        with col_right:
            with st.container(border=True, height=500):
                st.markdown("#### Lista de donantes")
                st.caption("Esta acción solo consulta datos en cadena y no consume firma de transacción.")

                # Input: dirección del contrato a consultar
                donor_contract = st.text_input("Contrato a consultar", placeholder="0x...", key="view_donors")
                st.write("")
                # Botón de acción destacado a ancho completo
                # Este botón solo hace lectura del contrato (no envía transacción).
                load_clicked = st.button("Cargar lista de donantes", use_container_width=True)

                # Área de resultados — ocupa el espacio restante del card
                st.divider()
                if load_clicked:
                    if donor_contract:
                        try:
                            # Llamada backend: get_donors_list() ejecuta una llamada .call().
                            donors = w3_manager.get_donors_list(donor_contract)
                            if donors:
                                for d in donors:
                                    st.code(d)
                            else:
                                st.info("Aún no hay donantes registrados en este contrato.")
                        except Exception as e:
                            st.error(f"No se pudo cargar la lista: {e}")
                    else:
                        st.warning("Introduce la dirección del contrato.")
                else:
                    st.caption("Los donantes aparecerán aquí tras cargar la lista.")
    else:
        with st.container(border=True):
            st.markdown("#### Balance")
            st.error("Conecta tu billetera en el menú lateral para ver tu balance y opciones.")

with tab2:
    # TAB 2: flujo de airdrop en dos pasos: aprobar y luego enviar.
    st.markdown("<div class='section-title'>Flujo de Airdrop</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-helper'>Paso 1: aprobación de gasto. Paso 2: ejecución del envío masivo.</div>", unsafe_allow_html=True)
    st.markdown("### Realizar airdrop")

    # Inputs base: dirección del contrato de airdrop y del token ERC-20.
    airdrop_contract = st.text_input("Airdrop Contract Address", placeholder="0x... (Despliégalo en la pestaña 3)")
    token_address = st.text_input("Token Address", placeholder="0x...")

    # --- Importar destinatarios desde CSV ---
    # pandas lee el archivo, validamos con Web3.is_address() y mostramos una tabla
    # con coloreado de filas inválidas antes de cargar en el formulario.
    with st.container(border=True):
        st.markdown("#### Importar destinatarios desde CSV")
        st.caption("Sube un CSV con columnas `address` y `amount` para cargar miles de destinatarios de golpe.")

        col_csv_info, col_csv_dl = st.columns([3, 1])
        with col_csv_dl:
            # CSV de ejemplo descargable para que el usuario vea el formato exacto
            sample_csv = "address,amount\n0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B,100\n0xCA35b7d915458EF540aDe6068dFe2F44E8fa733c,200"
            st.download_button(
                "📥 Descargar CSV ejemplo",
                data=sample_csv,
                file_name="ejemplo_airdrop.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_sample_csv"
            )

        uploaded_csv = st.file_uploader(
            "Seleccionar CSV",
            type=["csv"],
            key="csv_upload",
            help="Formato: columnas 'address' y 'amount'. La columna amount son unidades enteras (sin decimales)."
        )

        if uploaded_csv is not None:
            try:
                # pandas lee el CSV y normalizamos los nombres de columna
                df = pd.read_csv(uploaded_csv)
                df.columns = df.columns.str.strip().str.lower()

                # Comprobamos que existan las columnas obligatorias
                if "address" not in df.columns or "amount" not in df.columns:
                    st.error("❌ El CSV debe tener las columnas **address** y **amount**.")
                else:
                    # Limpieza de datos con pandas: quitamos NaN y normalizamos tipos
                    df = df[["address", "amount"]].dropna().reset_index(drop=True)
                    df["address"] = df["address"].str.strip()
                    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
                    df = df.dropna(subset=["amount"]).reset_index(drop=True)

                    # Validamos cada dirección Ethereum con web3 (sin gastar gas, es local)
                    df["válida"] = df["address"].apply(Web3.is_address)
                    df["estado"] = df["válida"].map({True: "✅ Válida", False: "❌ Inválida"})

                    # Métricas de calidad del CSV
                    total = len(df)
                    valid_count = int(df["válida"].sum())
                    invalid_count = total - valid_count

                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("Total filas", total)
                    col_m2.metric("✅ Válidas", valid_count)
                    col_m3.metric("❌ Inválidas", invalid_count)

                    if invalid_count > 0:
                        st.warning(f"⚠️ {invalid_count} dirección(es) inválida(s) — se excluirán al cargar en el formulario.")

                    # Tabla de previsualización con filas inválidas resaltadas en rojo
                    display_df = df[["address", "amount", "estado"]]
                    valid_series = df["válida"]

                    def highlight_invalid(row):
                        """Colorea en rojo las filas con dirección Ethereum no válida."""
                        if not valid_series.loc[row.name]:
                            return ["background-color: rgba(239,68,68,0.18)"] * len(row)
                        return [""] * len(row)

                    st.dataframe(
                        display_df.style.apply(highlight_invalid, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )

                    # Cargamos solo las filas válidas en el formulario manual (session_state)
                    if st.button("⬆️ Cargar en formulario", use_container_width=True, key="load_csv_btn"):
                        valid_df = df[df["válida"]]
                        # Guardamos en session_state: Streamlit usará estos valores
                        # como valor inicial de los text_area en el siguiente render
                        st.session_state["airdrop_recipients"] = ", ".join(valid_df["address"].tolist())
                        st.session_state["airdrop_amounts"] = ", ".join(
                            valid_df["amount"].apply(lambda x: str(int(x))).tolist()
                        )
                        st.rerun()

            except Exception as e:
                st.error(f"Error al leer el CSV: {e}")

    col_a, col_b = st.columns(2)
    with col_a:
        # Lista de receptores: rellena manualmente o carga desde el CSV de arriba.
        # La key "airdrop_recipients" permite que el botón CSV pre-rellene este campo.
        recipients = st.text_area("Recipients (comas)", placeholder="0x1..., 0x2...", height=100, key="airdrop_recipients")
    with col_b:
        # Lista de cantidades (unidades enteras, sin decimales): manual o desde CSV.
        amounts = st.text_area("Amounts (unidades)", placeholder="100, 200", height=100, key="airdrop_amounts")

    # --- Validación en tiempo real de direcciones ---
    # Streamlit rerenderiza en cada cambio de widget, así que esta validación
    # se ejecuta automáticamente cada vez que el usuario modifica el text_area.
    # Web3.is_address() es una función local (no llama al nodo), es instantánea.
    _hay_invalidas = False
    if recipients:
        _rcp_raw = [r.strip() for r in recipients.split(",") if r.strip()]
        if _rcp_raw:
            _validas   = [a for a in _rcp_raw if Web3.is_address(a)]
            _invalidas = [a for a in _rcp_raw if not Web3.is_address(a)]
            _hay_invalidas = len(_invalidas) > 0

            with st.container(border=True):
                st.markdown("#### 🔎 Validación de direcciones")
                st.caption("Se actualiza automáticamente al escribir. No consume gas.")
                _cv1, _cv2 = st.columns(2)
                with _cv1:
                    with st.container(border=True):
                        st.metric("✅ Válidas", len(_validas))
                with _cv2:
                    with st.container(border=True):
                        st.metric("❌ Inválidas", len(_invalidas))

                if _invalidas:
                    st.error("Las siguientes direcciones no son válidas. Corrígelas antes de enviar:")
                    # Mostramos cada inválida en su propia línea para que sea fácil localizarla
                    for _addr in _invalidas:
                        st.markdown(
                            f"<span style='color:#f87171;font-family:monospace;font-size:0.88rem;'>❌ {_addr}</span>",
                            unsafe_allow_html=True
                        )
                else:
                    st.success(f"Todas las direcciones son válidas ({len(_validas)}). Listo para enviar.")

    st.warning("Asegúrate de aprobar el contrato de airdrop antes de enviar.")

    # --- Estimación de gas ---
    # estimate_gas() es una llamada de solo lectura al nodo: simula la tx y devuelve
    # cuántas unidades de gas necesita, sin enviar nada ni gastar dinero real.
    with st.container(border=True):
        st.markdown("#### Estimar coste de gas")
        st.caption("Consulta cuánto ETH costará el airdrop antes de firmarlo. No envía ninguna transacción.")
        if st.button("🔍 Estimar gas", use_container_width=True, key="btn_estimate_gas"):
            if not airdrop_contract:
                st.warning("Falta la dirección del **Airdrop Contract** (campo al inicio del tab).")
            elif not token_address:
                st.warning("Falta la dirección del **Token Address** (campo al inicio del tab).")
            elif not recipients:
                st.warning("Falta la lista de **Recipients**.")
            elif not amounts:
                st.warning("Falta la lista de **Amounts**.")
            elif _hay_invalidas:
                st.warning("Corrige las direcciones inválidas antes de estimar.")
            elif not w3_manager.get_address():
                st.warning("Conecta tu wallet en el menú lateral.")
            else:
                try:
                    _rcp_est = [r.strip() for r in recipients.split(",") if r.strip()]
                    _amt_est = [int(a.strip()) * 10**18 for a in amounts.split(",") if a.strip()]
                    with st.spinner("Consultando el nodo..."):
                        # Llamada backend: estimate_airdrop_gas() no firma ni envía nada.
                        est = w3_manager.estimate_airdrop_gas(
                            airdrop_contract, token_address, _rcp_est, _amt_est
                        )
                    # Persistimos en session_state para que no desaparezca al rerenderizar
                    st.session_state["gas_estimate"] = est
                except Exception as e:
                    st.session_state["gas_estimate"] = None
                    st.error(f"No se pudo estimar: {e}")

        # Mostramos el resultado si ya existe en session_state
        if st.session_state.get("gas_estimate"):
            est = st.session_state["gas_estimate"]
            _cg1, _cg2, _cg3 = st.columns(3)
            with _cg1:
                with st.container(border=True):
                    st.metric("Unidades de gas", f"{est['gas_units']:,}")
                    st.caption("Esfuerzo computacional de la tx")
            with _cg2:
                with st.container(border=True):
                    st.metric("Precio del gas", f"{est['gas_price_gwei']} Gwei")
                    st.caption("Precio actual de mercado por unidad")
            with _cg3:
                with st.container(border=True):
                    st.metric("Coste total estimado", f"{est['cost_eth']:.8f} ETH")
                    st.caption("gas_units × gas_price")

    def centered_airdrop_action_buttons() -> tuple[bool, bool]:
        """Renderiza los dos botones de acción centrados y en horizontal."""
        _left, _center, _right = st.columns([1, 2, 1])
        with _center:
            btn_col_1, btn_col_2 = st.columns(2, gap="medium")
            with btn_col_1:
                approve_pressed = st.button("1. Aprobar airdrop", key="btn_approve_airdrop", use_container_width=True)
            with btn_col_2:
                send_pressed = st.button("2. Enviar airdrop", key="btn_send_airdrop", use_container_width=True)
        return approve_pressed, send_pressed

    # Botones de acción: centrados y lado a lado.
    approve_clicked, send_clicked = centered_airdrop_action_buttons()

    # Botón 1: aprueba que el contrato de airdrop pueda mover tokens del usuario.
    if approve_clicked:
        if not token_address or not airdrop_contract:
            logger.warning("Approve cancelado: faltan token_address o airdrop_contract")
            st.error("Faltan direcciones.")
        else:
            try:
                with st.spinner("Aprobando..."):
                    # Aprobamos una cantidad muy grande por simplicidad en el TFG
                    # Llamada backend: approve_airdrop() envía transacción al token.
                    tx = w3_manager.approve_airdrop(token_address, airdrop_contract, 10**24)
                    # Guardamos la aprobación en el historial SQLite
                    save_tx("Approve", tx, desde=w3_manager.get_address(), contrato=token_address)
                    st.success(f"¡Aprobación concedida!")
                    st.link_button("📜 Ver en Etherscan", f"https://sepolia.etherscan.io/tx/{tx}", use_container_width=True)
            except Exception as e:
                logger.error("Error en Approve — token: %s | error: %s", token_address, e)
                st.error(f"Error: {e}")

    # Botón 2: ejecuta el airdrop en cadena con receptores y montos.
    # Se bloquea si la validación en tiempo real detectó direcciones inválidas.
    if send_clicked:
        if not airdrop_contract or not token_address or not recipients or not amounts:
            logger.warning("Airdrop cancelado: campos incompletos")
            st.error("Rellena todos los campos.")
        elif _hay_invalidas:
            logger.warning("Airdrop cancelado: hay direcciones inválidas en la lista de receptores")
            st.error("Corrige las direcciones inválidas marcadas en rojo antes de enviar.")
        else:
            try:
                # Limpieza simple de texto para convertir inputs en listas utilizables.
                rcp_list = [r.strip() for r in recipients.split(",") if r.strip()]
                # Convertimos a unidades con 18 decimales
                amt_list = [int(a.strip()) * 10**18 for a in amounts.split(",") if a.strip()]
                logger.info("Iniciando airdrop — %d destinatarios | contrato: %s", len(rcp_list), airdrop_contract)

                with st.spinner("Enviando Airdrop..."):
                    # Llamada backend: send_airdrop() firma y envía la transacción del contrato.
                    tx = w3_manager.send_airdrop(airdrop_contract, token_address, rcp_list, amt_list)
                    # Guardamos el airdrop: tipo, hash, wallet firmante, contrato y nº destinatarios
                    save_tx("Airdrop", tx, desde=w3_manager.get_address(), contrato=airdrop_contract, destinatarios=len(rcp_list))

                    # Construimos el resultado como lista de dicts para el CSV de exportación.
                    # Cada destinatario comparte el mismo tx_hash porque es una sola transacción
                    # que el contrato procesa internamente en bucle.
                    st.session_state["ultimo_airdrop"] = [
                        {"address": addr, "tx_hash": tx, "status": "success"}
                        for addr in rcp_list
                    ]

                    st.success(f"Airdrop ejecutado con éxito")
                    st.code(tx, language=None)
                    st.link_button("📜 Ver en Etherscan", f"https://sepolia.etherscan.io/tx/{tx}", use_container_width=True)
                    st.balloons()
            except Exception as e:
                logger.error("Error en Airdrop — contrato: %s | error: %s", airdrop_contract, e)
                # Si falla, guardamos el resultado con status error para que también
                # sea exportable (útil para saber qué envíos fallaron)
                if recipients:
                    _rcp_err = [r.strip() for r in recipients.split(",") if r.strip()]
                    st.session_state["ultimo_airdrop"] = [
                        {"address": addr, "tx_hash": "-", "status": "error"}
                        for addr in _rcp_err
                    ]
                st.error(f"Error: {e}")

    # --- Exportar resultados del último airdrop a CSV ---
    # st.session_state["ultimo_airdrop"] se rellena al enviar (éxito o error).
    # Persiste mientras la sesión está abierta, así el usuario puede descargar
    # el CSV aunque haga scroll o cambie de pestaña.
    if st.session_state.get("ultimo_airdrop"):
        with st.container(border=True):
            st.markdown("#### 📤 Exportar resultado del airdrop")
            st.caption("CSV con cada dirección, el tx hash y el estado del envío.")

            # Convertimos la lista de dicts a DataFrame y luego a CSV con pandas
            df_result = pd.DataFrame(st.session_state["ultimo_airdrop"])
            csv_bytes = df_result.to_csv(index=False).encode("utf-8")

            # Tabla de previsualización antes de descargar
            st.dataframe(df_result, use_container_width=True, hide_index=True)

            st.download_button(
                "📥 Descargar CSV de resultados",
                data=csv_bytes,
                file_name="resultado_airdrop.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_result_csv"
            )

with tab3:
    # TAB 3: despliegue de contratos inteligentes desde la misma interfaz.
    st.markdown("<div class='section-title'>Deploy de Contratos</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-helper'>Publica contratos directamente desde la interfaz usando tu configuración Web3.</div>", unsafe_allow_html=True)
    
    # Inicializamos estado para que los resultados del deploy no desaparezcan al primer clic.
    if "last_deploy_token" not in st.session_state:
        st.session_state["last_deploy_token"] = None
    if "last_deploy_airdrop" not in st.session_state:
        st.session_state["last_deploy_airdrop"] = None

    st.markdown(
        "<div class='section-helper' style='text-align:center;margin-bottom:1.1rem;'>"
        "Elige qué contrato desplegar. Cada acción envía una transacción on-chain y guarda el resultado en el historial local."
        "</div>",
        unsafe_allow_html=True,
    )

    # Layout centrado: dos cards horizontales en columnas centrales.
    outer_left, col_token, col_airdrop, outer_right = st.columns([1, 4, 4, 1], gap="large")

    with col_token:
        with st.container(border=True):
            st.markdown("### 🪙 Cosa Token")
            st.caption("Contrato ERC-20 para emitir y transferir tokens de prueba en la red configurada.")
            st.markdown(
                "<div class='section-helper' style='margin-top:0.35rem;'>"
                "Ideal para preparar pruebas de distribución antes del airdrop masivo."
                "</div>",
                unsafe_allow_html=True,
            )

            btn_left, btn_center, btn_right = st.columns([1, 2, 1])
            with btn_center:
                # Botón de despliegue del contrato de token.
                if st.button("🚀 Lanzar token", key="deploy_token_btn", use_container_width=True):
                    try:
                        with st.spinner("Desplegando Token..."):
                            # Llamada backend: deploy_contract('CosaToken') publica el contrato.
                            res = w3_manager.deploy_contract('CosaToken')
                            # Guardamos el deploy del token en el historial
                            save_tx("Deploy Token", res['tx_hash'], desde=w3_manager.get_address(), contrato=res['address'])
                            st.session_state["last_deploy_token"] = res
                            st.balloons()
                    except Exception as e:
                        logger.error("Error desplegando CosaToken: %s", e)
                        st.error(f"Error: {e}")

            # Mostrar resultado persistente si existe
            if st.session_state["last_deploy_token"]:
                res = st.session_state["last_deploy_token"]
                st.markdown("---")
                st.markdown("<h3 style='text-align: center; color: #34d399;'>✅ TOKEN DESPLEGADO CON ÉXITO</h3>", unsafe_allow_html=True)
                st.markdown(f"<div style='background: rgba(52, 211, 153, 0.1); border: 2px solid #34d399; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;'><code style='font-size: 1.5rem; color: #34d399; word-break: break-all;'>{res['address']}</code></div>", unsafe_allow_html=True)
                st.code(res['address'], language=None)
                c1, c2 = st.columns(2)
                with c1:
                    st.link_button("🔍 Etherscan (Address)", f"https://sepolia.etherscan.io/address/{res['address']}", use_container_width=True)
                with c2:
                    st.link_button("📜 Etherscan (TX)", f"https://sepolia.etherscan.io/tx/{res['tx_hash']}", use_container_width=True)

    with col_airdrop:
        with st.container(border=True):
            st.markdown("### 🌐 Airdrop Contract")
            st.caption("Contrato de distribución masiva para enviar tokens a múltiples destinatarios en una sola transacción.")
            st.markdown(
                "<div class='section-helper' style='margin-top:0.35rem;'>"
                "Despliega este contrato y luego úsalo en la pestaña de Airdrop para ejecutar envíos en lote."
                "</div>",
                unsafe_allow_html=True,
            )

            btn_left, btn_center, btn_right = st.columns([1, 2, 1])
            with btn_center:
                # Botón de despliegue del contrato de airdrop.
                if st.button("⚡ Lanzar airdrop", key="deploy_airdrop_btn", use_container_width=True):
                    try:
                        with st.spinner("Desplegando Airdrop..."):
                            # Llamada backend: deploy_contract('Airdrop') publica el contrato.
                            res = w3_manager.deploy_contract('Airdrop')
                            # Guardamos el deploy del contrato airdrop en el historial
                            save_tx("Deploy Airdrop", res['tx_hash'], desde=w3_manager.get_address(), contrato=res['address'])
                            st.session_state["last_deploy_airdrop"] = res
                            st.balloons()
                    except Exception as e:
                        logger.error("Error desplegando Airdrop: %s", e)
                        st.error(f"Error: {e}")

            # Mostrar resultado persistente si existe
            if st.session_state["last_deploy_airdrop"]:
                res = st.session_state["last_deploy_airdrop"]
                st.markdown("---")
                st.markdown("<h3 style='text-align: center; color: #34d399;'>✅ AIRDROP DESPLEGADO CON ÉXITO</h3>", unsafe_allow_html=True)
                st.markdown(f"<div style='background: rgba(52, 211, 153, 0.1); border: 2px solid #34d399; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;'><code style='font-size: 1.5rem; color: #34d399; word-break: break-all;'>{res['address']}</code></div>", unsafe_allow_html=True)
                st.code(res['address'], language=None)
                c1, c2 = st.columns(2)
                with c1:
                    st.link_button("🔍 Etherscan (Address)", f"https://sepolia.etherscan.io/address/{res['address']}", use_container_width=True)
                with c2:
                    st.link_button("📜 Etherscan (TX)", f"https://sepolia.etherscan.io/tx/{res['tx_hash']}", use_container_width=True)

with tab4:
    # TAB 4: historial de transacciones persistidas en SQLite.
    # get_history() consulta la BD local y devuelve una lista de dicts que
    # convertimos a DataFrame de pandas para filtrar, mostrar y exportar.
    st.markdown("<div class='section-title'>Historial de Transacciones</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-helper'>Registro local de todas las transacciones enviadas desde esta app. Los datos se guardan en SQLite sin depender de la blockchain.</div>", unsafe_allow_html=True)
    st.markdown("### Registro de actividad")

    # Leemos todos los registros de la BD SQLite
    historial = get_history()

    if not historial:
        with st.container(border=True):
            st.info("Aún no hay transacciones registradas. Ejecuta un airdrop, deploy o donación para verlas aquí.")
    else:
        # Convertimos a DataFrame de pandas para poder filtrar y calcular métricas fácilmente
        df_hist = pd.DataFrame(historial)

        # --- Métricas resumen ---
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            with st.container(border=True):
                st.metric("Total txs", len(df_hist))
        with col_h2:
            with st.container(border=True):
                st.metric("Airdrops", int((df_hist["tipo"] == "Airdrop").sum()))
        with col_h3:
            with st.container(border=True):
                total_dest = df_hist["destinatarios"].dropna().sum()
                st.metric("Destinatarios totales", int(total_dest))
        with col_h4:
            with st.container(border=True):
                st.metric("Deploys", int(df_hist["tipo"].str.startswith("Deploy").sum()))

        # --- Filtro por tipo de operación ---
        tipos_disponibles = ["Todos"] + sorted(df_hist["tipo"].unique().tolist())
        filtro = st.selectbox("Filtrar por tipo", tipos_disponibles, key="hist_filter")
        if filtro != "Todos":
            df_hist = df_hist[df_hist["tipo"] == filtro]

        # --- Tabla principal ---
        with st.container(border=True):
            st.markdown("#### Transacciones")
            df_display = df_hist.copy()
            # Acortamos el hash para que quepa en la tabla pero mantenemos el completo para el link
            df_display["tx_hash_corto"] = df_display["tx_hash"].apply(
                lambda h: f"{h[:10]}...{h[-6:]}" if isinstance(h, str) and len(h) > 16 else h
            )
            df_display["etherscan"] = df_display["tx_hash"].apply(
                lambda h: f"https://sepolia.etherscan.io/tx/{h}" if isinstance(h, str) else ""
            )
            columnas = ["fecha", "tipo", "estado", "destinatarios", "tx_hash_corto", "etherscan", "desde", "contrato"]
            columnas_presentes = [c for c in columnas if c in df_display.columns]
            st.dataframe(
                df_display[columnas_presentes],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "etherscan": st.column_config.LinkColumn("🔗 Etherscan", display_text="Ver tx"),
                    "tx_hash_corto": st.column_config.TextColumn("TX Hash"),
                    "fecha": st.column_config.TextColumn("Fecha"),
                    "tipo": st.column_config.TextColumn("Tipo"),
                    "estado": st.column_config.TextColumn("Estado"),
                    "destinatarios": st.column_config.NumberColumn("Destinatarios"),
                    "desde": st.column_config.TextColumn("Wallet"),
                    "contrato": st.column_config.TextColumn("Contrato"),
                }
            )

        # --- Exportar historial como CSV ---
        # to_csv() de pandas convierte el DataFrame a texto CSV para descargarlo
        csv_export = df_hist.drop(columns=["id"], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Exportar historial CSV",
            data=csv_export,
            file_name="historial_txs.csv",
            mime="text/csv",
            use_container_width=True,
            key="export_hist_csv"
        )

with tab5:
    # TAB 5: visor de logs en tiempo real.
    #
    # El módulo `logging` escribe cada operación en tsender.log.
    # Aquí simplemente leemos ese archivo con open() (stdlib de Python, sin librerías extra)
    # y lo mostramos con st.code() para que se vea con formato monoespacio.
    #
    # Niveles de log que verás en el archivo:
    #   DEBUG    → consultas internas (ej: historial leído de BD)
    #   INFO     → operaciones completadas con éxito (deploy, airdrop, etc.)
    #   WARNING  → acciones canceladas por el usuario (campos vacíos, etc.)
    #   ERROR    → excepciones capturadas (tx fallida, nodo no responde, etc.)

    st.markdown("<div class='section-title'>Logs del sistema</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-helper'>Registro de todas las operaciones generadas por el módulo <code>logging</code> de Python. "
        "Se guarda en <code>tsender.log</code> junto al código fuente.</div>",
        unsafe_allow_html=True
    )

    # ── Controles ───────────────────────────────────────────────────────────
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 1])

    with col_ctrl1:
        # Filtra por nivel de log. El módulo logging usa estos 5 niveles estándar.
        nivel_filter = st.selectbox(
            "Filtrar por nivel",
            ["Todos", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            key="log_nivel"
        )

    with col_ctrl2:
        # Número de líneas a mostrar (las más recientes, desde el final del archivo).
        max_lines = st.number_input(
            "Últimas N líneas", min_value=10, max_value=1000, value=100, step=10,
            key="log_max_lines",
            help="El archivo crece hacia abajo; las últimas líneas son las más recientes."
        )

    with col_ctrl3:
        st.write("")  # espaciado vertical para alinear el botón
        st.write("")
        # Streamlit no actualiza la página automáticamente; este botón fuerza un rerun
        # para volver a leer el archivo y mostrar los últimos mensajes.
        if st.button("🔄 Actualizar", use_container_width=True, key="log_refresh"):
            logger.debug("Visor de logs actualizado manualmente por el usuario")
            st.rerun()

    # ── Lectura del archivo ──────────────────────────────────────────────────
    # Comprobamos si el archivo existe. La primera vez que se arranca la app
    # puede que todavía no se haya generado ningún mensaje.
    if not os.path.exists(LOG_PATH):
        with st.container(border=True):
            st.info(
                "El archivo `tsender.log` aún no existe. "
                "Realiza cualquier operación (deploy, airdrop, donación…) para generarlo."
            )
    else:
        # open() con encoding='utf-8' para leer correctamente acentos.
        # readlines() devuelve una lista donde cada elemento es una línea del archivo.
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            todas_las_lineas = f.readlines()

        # Aplicamos el filtro por nivel: buscamos el texto del nivel en cada línea.
        # El formato del Formatter es: "YYYY-MM-DD HH:MM:SS | NIVEL    | modulo | mensaje"
        if nivel_filter != "Todos":
            lineas_filtradas = [l for l in todas_las_lineas if f"| {nivel_filter}" in l]
        else:
            lineas_filtradas = todas_las_lineas

        # Recortamos a las últimas N líneas para no sobrecargar el navegador.
        # El operador de slicing negativo [-n:] devuelve los últimos n elementos.
        lineas_visibles = lineas_filtradas[-int(max_lines):]

        # ── Métricas rápidas ─────────────────────────────────────────────────
        col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
        total_lineas = len(todas_las_lineas)

        def _count_level(lines, level):
            """Cuenta cuántas líneas contienen un nivel de log concreto."""
            return sum(1 for l in lines if f"| {level}" in l)

        with col_m1:
            with st.container(border=True):
                st.metric("Total entradas", total_lineas)
        with col_m2:
            with st.container(border=True):
                st.metric("INFO", _count_level(todas_las_lineas, "INFO"))
        with col_m3:
            with st.container(border=True):
                st.metric("DEBUG", _count_level(todas_las_lineas, "DEBUG"))
        with col_m4:
            with st.container(border=True):
                st.metric("WARNING", _count_level(todas_las_lineas, "WARNING"))
        with col_m5:
            with st.container(border=True):
                st.metric("ERROR", _count_level(todas_las_lineas, "ERROR"))

        # ── Visor ────────────────────────────────────────────────────────────
        with st.container(border=True):
            if lineas_visibles:
                st.caption(
                    f"Mostrando {len(lineas_visibles)} de {len(lineas_filtradas)} entradas "
                    f"({'todas' if nivel_filter == 'Todos' else nivel_filter}) — "
                    f"archivo: `{LOG_PATH}`"
                )
                # st.code() renderiza el texto con fuente monoespaciada y resaltado.
                # language=None desactiva el coloreado de sintaxis para que no confunda.
                st.code("".join(lineas_visibles), language=None)
            else:
                st.info(f"No hay entradas de nivel **{nivel_filter}** en el archivo de log.")

        # ── Descargar log completo ────────────────────────────────────────────
        with open(LOG_PATH, 'rb') as f_raw:
            log_bytes = f_raw.read()

        st.download_button(
            "📥 Descargar tsender.log completo",
            data=log_bytes,
            file_name="tsender.log",
            mime="text/plain",
            use_container_width=True,
            key="download_log"
        )

with tab6:
    # TAB 6: Dashboard de estadísticas con gráficas usando Plotly.
    #
    # Plotly es una librería de visualización interactiva.
    # Nota: Aunque Streamlit la soporta nativamente, la librería 'plotly' debe 
    # estar instalada en el entorno virtual (pip install plotly).
    #
    # Flujo de datos:
    #   SQLite (historial.db) → get_history() → lista de dicts
    #   → DataFrame de pandas → gráficas Plotly → st.plotly_chart()
    #
    # Este tab combina tres conceptos de Python muy valorados en clase:
    #   1. Consulta a base de datos (sqlite3 a través de db.py)
    #   2. Transformación de datos con pandas (groupby, value_counts, resample)
    #   3. Visualización con plotly (bar chart, pie chart, line chart)

    import plotly.graph_objects as go
    import plotly.express as px

    st.markdown("<div class='section-title'>Estadísticas</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-helper'>Visualización interactiva de la actividad on-chain. "
        "Datos obtenidos de la base de datos local SQLite y procesados con pandas.</div>",
        unsafe_allow_html=True
    )

    # Leemos el historial de SQLite — misma fuente que la pestaña Historial.
    datos = get_history()

    if not datos:
        with st.container(border=True):
            st.info("Aún no hay transacciones registradas. Ejecuta un airdrop, deploy o donación para ver las estadísticas.")
    else:
        # ── Preparación del DataFrame ────────────────────────────────────────
        # Convertimos la lista de dicts a DataFrame de pandas.
        # pd.to_datetime() transforma la columna 'fecha' (string) a tipo datetime,
        # lo que permite agrupar por día, semana, etc. con dt.date.
        df = pd.DataFrame(datos)
        df["fecha_dt"] = pd.to_datetime(df["fecha"])
        df["dia"] = df["fecha_dt"].dt.date  # solo la fecha, sin la hora

        # ── Fila 1: métricas rápidas ─────────────────────────────────────────
        col_e1, col_e2, col_e3, col_e4 = st.columns(4)

        total_txs       = len(df)
        total_exito     = int((df["estado"] == "éxito").sum())
        total_error     = int((df["estado"] == "error").sum())
        total_dest      = int(df["destinatarios"].dropna().sum())

        with col_e1:
            with st.container(border=True):
                st.metric("Total transacciones", total_txs)
        with col_e2:
            with st.container(border=True):
                st.metric("✅ Éxito", total_exito)
        with col_e3:
            with st.container(border=True):
                st.metric("❌ Error", total_error)
        with col_e4:
            with st.container(border=True):
                st.metric("Wallets alcanzadas", total_dest)

        # ── Fila 2: gráfico de barras + pie chart ────────────────────────────
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            with st.container(border=True):
                st.markdown("#### Transacciones por tipo")
                st.caption("value_counts() de pandas cuenta cuántas veces aparece cada tipo en la columna.")

                # value_counts() devuelve una Series con el conteo de cada valor único.
                # reset_index() la convierte en DataFrame para que plotly la pueda leer.
                conteo_tipo = df["tipo"].value_counts().reset_index()
                conteo_tipo.columns = ["tipo", "cantidad"]

                # go.Bar: gráfico de barras de Plotly.
                # x = categorías (tipo de tx), y = valores (cantidad).
                fig_bar = go.Figure(
                    go.Bar(
                        x=conteo_tipo["tipo"],
                        y=conteo_tipo["cantidad"],
                        marker=dict(
                            color=conteo_tipo["cantidad"],
                            colorscale=[[0, "#0ea5e9"], [1, "#22d3ee"]],
                            showscale=False,
                            line=dict(color="rgba(34,211,238,0.4)", width=1)
                        ),
                        text=conteo_tipo["cantidad"],
                        textposition="outside",
                        textfont=dict(color="#e5e7eb", size=13)
                    )
                )
                fig_bar.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(11,15,26,0.6)",
                    font=dict(color="#e5e7eb", family="Manrope"),
                    xaxis=dict(
                        gridcolor="rgba(34,211,238,0.08)",
                        tickfont=dict(color="#9ca3af")
                    ),
                    yaxis=dict(
                        gridcolor="rgba(34,211,238,0.08)",
                        tickfont=dict(color="#9ca3af")
                    ),
                    margin=dict(t=20, b=20, l=10, r=10),
                    height=300
                )
                # st.plotly_chart renderiza la figura Plotly como HTML interactivo.
                # use_container_width=True hace que se adapte al ancho del panel.
                st.plotly_chart(fig_bar, use_container_width=True)

        with col_g2:
            with st.container(border=True):
                st.markdown("#### Éxito vs Error")
                st.caption("Proporción de transacciones exitosas frente a fallidas.")

                # Contamos por estado (éxito / error).
                conteo_estado = df["estado"].value_counts().reset_index()
                conteo_estado.columns = ["estado", "cantidad"]

                # go.Pie: gráfico de tarta. labels = categorías, values = valores.
                # hole=0.45 crea un donut chart (hueco central), más moderno visualmente.
                fig_pie = go.Figure(
                    go.Pie(
                        labels=conteo_estado["estado"],
                        values=conteo_estado["cantidad"],
                        hole=0.45,
                        marker=dict(
                            colors=["#34d399", "#f87171"],
                            line=dict(color="#0b0f1a", width=2)
                        ),
                        textfont=dict(color="#e5e7eb", size=13),
                        insidetextorientation="radial"
                    )
                )
                fig_pie.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#e5e7eb", family="Manrope"),
                    legend=dict(
                        font=dict(color="#9ca3af"),
                        bgcolor="rgba(0,0,0,0)"
                    ),
                    margin=dict(t=20, b=20, l=10, r=10),
                    height=300
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # ── Fila 3: línea temporal de actividad ──────────────────────────────
        with st.container(border=True):
            st.markdown("#### Actividad por día")
            st.caption(
                "groupby('dia') agrupa todas las filas con la misma fecha y "
                "size() cuenta cuántas hay. El resultado es una Serie indexada por fecha."
            )

            # groupby('dia'): agrupa filas por fecha.
            # size(): cuenta el número de filas de cada grupo (= txs de ese día).
            # reset_index(): convierte la Serie en DataFrame.
            # rename(): renombra la columna 0 → 'txs' para que el eje Y tenga nombre.
            txs_por_dia = (
                df.groupby("dia")
                .size()
                .reset_index()
                .rename(columns={0: "txs"})
            )

            # px.line: gráfico de línea de Plotly Express (API de alto nivel).
            # markers=True añade un punto en cada fecha con dato.
            fig_line = px.line(
                txs_por_dia,
                x="dia",
                y="txs",
                markers=True,
                labels={"dia": "Fecha", "txs": "Transacciones"},
            )
            fig_line.update_traces(
                line=dict(color="#22d3ee", width=2.5),
                marker=dict(color="#22d3ee", size=8,
                            line=dict(color="#0b0f1a", width=2))
            )
            fig_line.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(11,15,26,0.6)",
                font=dict(color="#e5e7eb", family="Manrope"),
                xaxis=dict(
                    gridcolor="rgba(34,211,238,0.08)",
                    tickfont=dict(color="#9ca3af")
                ),
                yaxis=dict(
                    gridcolor="rgba(34,211,238,0.08)",
                    tickfont=dict(color="#9ca3af"),
                    tickformat="d"          # enteros, sin decimales en el eje Y
                ),
                margin=dict(t=20, b=20, l=10, r=10),
                height=280
            )
            st.plotly_chart(fig_line, use_container_width=True)

        # ── Fila 4: destinatarios por airdrop ────────────────────────────────
        # Solo tiene sentido si hay al menos un airdrop con destinatarios registrados.
        df_airdrops = df[(df["tipo"] == "Airdrop") & (df["destinatarios"].notna())].copy()

        if not df_airdrops.empty:
            with st.container(border=True):
                st.markdown("#### Destinatarios por airdrop")
                st.caption("Cada barra es un airdrop distinto. El eje Y muestra cuántas wallets recibieron tokens.")

                # Formateamos el eje X con fecha + hash corto para identificar cada airdrop.
                df_airdrops["etiqueta"] = (
                    df_airdrops["fecha"].str[:10] + " · " +
                    df_airdrops["tx_hash"].str[:8] + "..."
                )

                fig_dest = go.Figure(
                    go.Bar(
                        x=df_airdrops["etiqueta"],
                        y=df_airdrops["destinatarios"].astype(int),
                        marker=dict(
                            color=df_airdrops["destinatarios"].astype(int),
                            colorscale=[[0, "#0ea5e9"], [1, "#34d399"]],
                            showscale=False,
                            line=dict(color="rgba(34,211,238,0.3)", width=1)
                        ),
                        text=df_airdrops["destinatarios"].astype(int),
                        textposition="outside",
                        textfont=dict(color="#e5e7eb", size=12)
                    )
                )
                fig_dest.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(11,15,26,0.6)",
                    font=dict(color="#e5e7eb", family="Manrope"),
                    xaxis=dict(
                        gridcolor="rgba(34,211,238,0.08)",
                        tickfont=dict(color="#9ca3af"),
                        tickangle=-30
                    ),
                    yaxis=dict(
                        gridcolor="rgba(34,211,238,0.08)",
                        tickfont=dict(color="#9ca3af"),
                        tickformat="d"
                    ),
                    margin=dict(t=20, b=60, l=10, r=10),
                    height=300
                )
                st.plotly_chart(fig_dest, use_container_width=True)
