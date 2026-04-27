import streamlit as st
import time
from web3_utils import Web3Manager
import os
from dotenv import load_dotenv

# Carga variables del archivo .env (si existe) para no escribir secretos en el código.
load_dotenv()

# Configuración general de la página de Streamlit (título, icono y ancho del layout).
st.set_page_config(page_title="TSender", page_icon="🚀", layout="centered")

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

    .stApp {
        background:
            radial-gradient(900px 380px at 50% -8%, rgba(14, 165, 233, 0.16), transparent 62%),
            linear-gradient(180deg, var(--bg-0) 0%, var(--bg-1) 100%);
        color: var(--text);
        font-family: 'Manrope', sans-serif;
    }

    * {
        transition: all 0.2s ease;
    }

    .block-container {
        max-width: 1140px;
        padding-top: 1.8rem;
        padding-bottom: 2.4rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(11, 15, 26, 0.97), rgba(11, 15, 26, 0.94));
        border-right: 1px solid rgba(34, 211, 238, 0.2);
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label {
        color: var(--text) !important;
    }

    section[data-testid="stSidebar"] h2 {
        color: var(--text) !important;
    }

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
        transition: box-shadow 0.25s ease, border-color 0.25s ease, transform 0.25s ease;
    }

    .header-container::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: inherit;
        pointer-events: none;
        opacity: 0.55;
        background: radial-gradient(700px 120px at 50% 0%, rgba(34, 211, 238, 0.16), transparent 70%);
        transition: opacity 0.25s ease;
    }

    .header-container:hover {
        border-color: rgba(34, 211, 238, 0.35);
        transform: translateY(-1px);
        box-shadow:
            0 26px 52px rgba(2, 8, 23, 0.36),
            0 0 0 1px rgba(34, 211, 238, 0.16),
            0 0 26px rgba(34, 211, 238, 0.25);
    }

    .header-container:hover::before {
        opacity: 0.9;
    }

    .header-left,
    .header-center,
    .header-right {
        display: flex;
        align-items: center;
    }

    .header-center {
        flex: 1;
        justify-content: center;
    }

    .header-right {
        justify-content: flex-end;
    }

    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 0.7rem;
    }

    .brand-mark {
        width: 38px;
        height: 38px;
        border-radius: 999px;
        position: relative;
        overflow: hidden;
        isolation: isolate;
        background: linear-gradient(135deg, #0ea5e9, #22d3ee);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5px;
        color: white;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: -0.25px;
        line-height: 1;
        box-shadow:
            0 10px 20px rgba(34, 211, 238, 0.24),
            0 0 0 1px rgba(34, 211, 238, 0.32),
            0 0 14px rgba(34, 211, 238, 0.2);
    }

    .brand-mark::before {
        content: "";
        position: absolute;
        inset: 2px;
        border-radius: 999px;
        background: linear-gradient(180deg, rgba(11, 15, 26, 0.98), rgba(11, 15, 26, 0.8));
        z-index: 1;
    }

    .logo-t {
        color: #ffffff;
        display: inline-block;
        transform: none;
        position: relative;
        z-index: 2;
    }

    .logo-s {
        color: #ffffff;
        display: inline-block;
        transform: none;
        position: relative;
        z-index: 2;
        opacity: 0.95;
    }

    .logo-text {
        font-size: 1.2rem;
        font-weight: 800;
        letter-spacing: 0.48px;
        color: var(--text);
        text-transform: uppercase;
    }

    .nav-links {
        display: flex;
        gap: 0.6rem;
        font-size: 0.74rem;
        color: var(--text);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.88px;
    }

    .nav-pill {
        padding: 0.46rem 0.82rem;
        border-radius: 999px;
        border: 1px solid rgba(34, 211, 238, 0.2);
        background: rgba(11, 15, 26, 0.55);
        color: var(--text);
        transition: all 0.22s ease;
    }

    .nav-pill:hover {
        border-color: rgba(34, 211, 238, 0.34);
        box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.2), 0 0 12px rgba(34, 211, 238, 0.18);
        filter: brightness(1.04);
    }

    .connect-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.24), rgba(34, 211, 238, 0.18));
        border: 1px solid rgba(34, 211, 238, 0.34);
        color: var(--text);
        padding: 0.54rem 0.9rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.76rem;
        letter-spacing: 0.56px;
        text-transform: uppercase;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12);
    }

    .wallet-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #22d3ee;
        box-shadow: 0 0 0 4px rgba(34, 211, 238, 0.2), 0 0 10px rgba(34, 211, 238, 0.25);
    }

    .hero-wrap {
        position: relative;
        margin-bottom: 1.35rem;
    }

    .hero-wrap::before {
        content: "";
        position: absolute;
        width: 76%;
        height: 170px;
        left: 12%;
        top: -28px;
        background: radial-gradient(closest-side, rgba(34, 211, 238, 0.25), transparent 72%);
        filter: blur(10px);
        pointer-events: none;
    }

    .main-card {
        --x: 50%;
        --y: 50%;
        position: relative;
        background: linear-gradient(145deg, var(--card) 0%, var(--panel-2) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(34, 211, 238, 0.28);
        border-radius: 18px;
        padding: 3.2rem 2.2rem;
        text-align: center;
        margin-bottom: 0;
        margin-top: 1rem;
        overflow: hidden;
        box-shadow: 0 28px 56px rgba(2, 8, 23, 0.42);
        transition: transform 220ms ease, box-shadow 260ms ease, border-color 220ms ease;
    }

    .main-card::before {
        content: "";
        position: absolute;
        inset: 0;
        opacity: 0;
        background:
            radial-gradient(260px 220px at var(--x) var(--y), rgba(34, 211, 238, 0.25), rgba(34, 211, 238, 0.12) 38%, rgba(0, 0, 0, 0) 70%);
        transition: opacity 240ms ease;
        pointer-events: none;
        z-index: 1;
    }

    .main-card::after {
        content: "";
        position: absolute;
        inset: 0;
        background:
            radial-gradient(500px 230px at 10% -20%, rgba(14, 165, 233, 0.12), transparent 60%),
            radial-gradient(440px 230px at 92% 118%, rgba(34, 211, 238, 0.1), transparent 60%);
        pointer-events: none;
        z-index: 0;
    }

    .main-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(34, 211, 238, 0.45);
        box-shadow: 0 34px 66px rgba(2, 8, 23, 0.5), 0 0 26px rgba(34, 211, 238, 0.25);
    }

    .main-card:hover::before {
        opacity: 1;
    }

    .gradient-text {
        position: relative;
        z-index: 2;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.12;
        letter-spacing: -0.55px;
        background: linear-gradient(90deg, #e5e7eb 0%, #22d3ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.85rem;
    }

    .subtitle {
        position: relative;
        z-index: 2;
        color: var(--text);
        font-size: 1.08rem;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.55;
    }

    .ui-kicker {
        position: relative;
        z-index: 2;
        color: var(--accent);
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 1.6px;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .section-title {
        font-size: 1.15rem;
        color: var(--text);
        font-weight: 700;
        letter-spacing: 0.25px;
        margin: 0.25rem 0 0.35rem 0;
    }

    .section-helper {
        color: var(--muted);
        font-size: 0.93rem;
        margin-bottom: 0.9rem;
        line-height: 1.45;
    }

    [data-testid="stTabPanel"] [data-testid="stVerticalBlock"] > div {
        border-radius: 14px;
    }

    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stTabPanel"] [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        position: relative;
        background: rgba(11, 15, 26, 0.7);
        border: 1px solid rgba(34, 211, 238, 0.25) !important;
        border-radius: 16px !important;
        padding: 0.24rem 0.24rem 0.1rem 0.24rem;
        margin: 0 0 1rem 0;
        box-shadow: 0 12px 26px rgba(2, 8, 23, 0.34), 0 0 12px rgba(34, 211, 238, 0.11);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
        overflow: hidden;
    }

    [data-testid="stVerticalBlockBorderWrapper"]::before {
        content: "";
        position: absolute;
        inset: 0;
        pointer-events: none;
        background:
            radial-gradient(560px 120px at 10% -10%, rgba(34, 211, 238, 0.12), transparent 65%),
            radial-gradient(420px 190px at 95% 110%, rgba(14, 165, 233, 0.1), transparent 68%);
        opacity: 0.75;
        transition: opacity 0.2s ease;
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover,
    [data-testid="stTabPanel"] [data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        border-color: rgba(34, 211, 238, 0.44) !important;
        box-shadow: 0 16px 30px rgba(2, 8, 23, 0.38), 0 0 22px rgba(34, 211, 238, 0.2);
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover::before {
        opacity: 1;
    }

    [data-testid="stVerticalBlockBorderWrapper"] h4 {
        font-size: 1.28rem !important;
        font-weight: 800 !important;
        margin-bottom: 0.2rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] p {
        line-height: 1.45;
    }

    h3 {
        color: var(--text) !important;
        font-size: 1.62rem !important;
    }

    h4 {
        color: var(--text) !important;
        font-size: 1.24rem !important;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 14px;
    }

    [data-baseweb="tab-list"] {
        justify-content: center;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        gap: 0.6rem;
        background: rgba(11, 15, 26, 0.7);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 0.42rem;
        margin-top: 0.5rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 14px 32px rgba(2, 8, 23, 0.32);
    }

    [data-baseweb="tab"] {
        position: relative;
        background: rgba(11, 15, 26, 0.55) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
        font-weight: 700 !important;
        border: 1px solid rgba(34, 211, 238, 0.18) !important;
        transition: all 0.2s ease;
        padding: 0.58rem 1rem !important;
        min-width: 155px;
        text-align: center;
    }

    /* Oculta el indicador por defecto (a veces aparece rojo según tema/baseweb). */
    [data-baseweb="tab-highlight"] {
        background-color: transparent !important;
        box-shadow: none !important;
        opacity: 0 !important;
    }

    [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.3), rgba(34, 211, 238, 0.22)) !important;
        color: var(--text) !important;
        border-color: rgba(34, 211, 238, 0.46) !important;
        box-shadow: 0 10px 22px rgba(34, 211, 238, 0.25);
    }

    [data-baseweb="tab"][aria-selected="true"]::after {
        content: "";
        position: absolute;
        left: 14px;
        right: 14px;
        bottom: 6px;
        height: 2px;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(34, 211, 238, 0.6), rgba(34, 211, 238, 1));
        box-shadow: 0 0 12px rgba(34, 211, 238, 0.35);
    }

    [data-baseweb="tab"]:hover {
        filter: brightness(1.06);
    }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: linear-gradient(180deg, rgba(11, 15, 26, 0.95), rgba(11, 15, 26, 0.84)) !important;
        color: var(--text) !important;
        border: 1px solid rgba(34, 211, 238, 0.25) !important;
        border-radius: 10px !important;
        min-height: 2.85rem;
        padding-left: 0.8rem !important;
    }

    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus,
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(34, 211, 238, 0.66) !important;
        box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.25) !important;
        outline: none !important;
    }

    .stTextArea textarea {
        min-height: 112px !important;
    }

    [data-baseweb="input"] {
        background: rgba(11, 15, 26, 0.9) !important;
        border: 1px solid rgba(34, 211, 238, 0.25) !important;
        border-radius: 10px !important;
    }

    [data-baseweb="input"]:focus-within {
        border-color: rgba(34, 211, 238, 0.66) !important;
        box-shadow: 0 0 0 2px rgba(34, 211, 238, 0.2) !important;
    }

    [data-testid="stButton"] button,
    div.stButton > button:first-child {
        background: linear-gradient(135deg, var(--brand-1), var(--brand-2));
        color: var(--text);
        font-weight: 800;
        border: 1px solid rgba(34, 211, 238, 0.34);
        width: 100%;
        padding: 0.8rem 1.1rem;
        border-radius: 10px;
        transition: all 0.2s ease;
        margin-top: 0.95rem;
        box-shadow: 0 14px 26px rgba(34, 211, 238, 0.25);
        letter-spacing: 0.2px;
    }

    [data-testid="stButton"] button:hover,
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        filter: brightness(1.1);
        box-shadow: 0 18px 30px rgba(34, 211, 238, 0.3), 0 0 18px rgba(34, 211, 238, 0.22);
        color: var(--text);
    }

    [data-testid="stButton"] button:active,
    div.stButton > button:first-child:active {
        transform: translateY(1px);
        filter: brightness(0.98);
        box-shadow: 0 8px 16px rgba(34, 211, 238, 0.22);
    }

    .stTextInput label,
    .stTextArea label,
    .stNumberInput label {
        color: var(--text) !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--success);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(34, 211, 238, 0.24) !important;
        background: linear-gradient(160deg, rgba(11, 15, 26, 0.92), rgba(11, 15, 26, 0.78)) !important;
        color: var(--text) !important;
        box-shadow: 0 8px 18px rgba(2, 8, 23, 0.28);
    }

    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
        color: var(--text) !important;
    }

    .stCodeBlock,
    .stCode {
        border-radius: 10px;
        border: 1px solid rgba(34, 211, 238, 0.22);
    }

    hr {
        display: none !important;
    }

    .stSuccess {
        border-color: rgba(52, 211, 153, 0.45) !important;
    }

    .stSuccess [data-testid="stMarkdownContainer"] {
        color: var(--success) !important;
    }

    @media (max-width: 900px) {
        .header-container {
            padding: 0.9rem;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.75rem;
        }

        .header-center {
            width: 100%;
            justify-content: flex-start;
        }

        .header-right {
            width: 100%;
            justify-content: flex-start;
        }

        .nav-links {
            flex-wrap: wrap;
        }

        [data-baseweb="tab"] {
            min-width: 112px;
        }

        .gradient-text {
            font-size: 2.08rem;
        }

        .subtitle {
            font-size: 0.98rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# --- Siderbar: Configuración Web3 ---
# Sidebar: aquí el usuario configura conexión y credenciales.
# Todo lo que se escriba en inputs se vuelve a evaluar al recargar la app.
with st.sidebar:
    st.header("Configuración Web3")
    st.info("Dado que esto es Python puro vamos a inyectar la URL del nodo (RPC) y la Private Key directamente.")

    # Input 1: URL RPC del nodo al que nos conectamos (por defecto Sepolia).
    rpc_url = st.text_input("RPC URL", value=os.getenv("RPC_URL", "https://rpc.sepolia.org"))
    # Input 2: clave privada para firmar transacciones desde la billetera.
    private_key = st.text_input("Private Key", type="password", value=os.getenv("PRIVATE_KEY", ""))

    # Punto de unión frontend-backend: crea el gestor Web3 con los datos del usuario.
    # A partir de aquí, el frontend llama métodos de Web3Manager para consultar/enviar transacciones.
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
# Tarjeta de bienvenida: componente informativo, solo visual.
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
tab1, tab2, tab3 = st.tabs(["Dashboard", "Airdrop", "Deploy"])

with tab1:
    # TAB 1: panel de estado, donaciones y lectura de donantes.
    st.markdown("<div class='section-title'>Resumen de Cuenta</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-helper'>Consulta tu wallet, revisa contratos y gestiona donaciones desde un único panel.</div>", unsafe_allow_html=True)
    st.markdown("### Tu balance y estado")
    # Si no hay wallet, se bloquean acciones que requieren firma de transacción.
    if w3_manager.get_address():
        with st.container(border=True):
            st.markdown("#### Balance")
            st.caption("Estado de tu wallet y consulta rápida de contratos.")
            col_main1, col_main2 = st.columns(2)
            with col_main1:
                # Datos básicos de la cuenta actual (lectura desde backend).
                st.info(f"**Billetera Configurada:**\n`{w3_manager.get_address()}`")
                st.success(f"**Tus Fondos:** {float(w3_manager.get_balance()):.4f} ETH")

            with col_main2:
                # Input para consultar el balance ETH de un contrato concreto.
                contract_to_check = st.text_input("Dirección del Contrato (Airdrop/Donación)", placeholder="0x...", key="check_balance")
                if contract_to_check:
                    try:
                        # Llamada backend: get_contract_eth_balance() solo lee estado en cadena.
                        c_balance = w3_manager.get_contract_eth_balance(contract_to_check)
                        st.metric("Balance del Contrato", f"{float(c_balance):.4f} ETH")
                    except:
                        st.error("Dirección no válida")

        # --- SECCIÓN DE DONACIONES ---
        with st.container(border=True):
            st.markdown("#### Donaciones")
            st.caption("Introduce contrato y monto. Al confirmar, se firma y envía una transacción en blockchain.")
            st.markdown("#### Realizar donación al contrato")
            col_don1, col_don2 = st.columns([2, 1])
            with col_don1:
                # Inputs de donación: contrato destino + cantidad en ETH.
                target_contract = st.text_input("Dirección Contrato Destino", placeholder="0x...", key="donate_addr")
                donation_amount = st.number_input("Cantidad a donar (ETH)", min_value=0.0001, format="%.4f")
            with col_don2:
                st.write("")  # Espaciador
                # Al pulsar este botón se firma y envía una transacción real de ETH.
                if st.button("Donar ahora"):
                    if target_contract:
                        try:
                            with st.spinner("Procesando donación..."):
                                # Llamada backend: donate_eth() construye, firma y envía la transacción.
                                tx = w3_manager.donate_eth(target_contract, donation_amount)
                                st.success(f"¡Donación exitosa! TX: {tx[:10]}...")
                                st.balloons()
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Pon la dirección del contrato.")

        # --- SECCIÓN DE LISTA DE DONANTES ---
        with st.container(border=True):
            st.markdown("#### Lista de donantes")
            st.caption("Esta acción solo consulta datos en cadena y no consume firma de transacción.")
            st.markdown("#### Libro de donantes")
            # Input para indicar de qué contrato queremos leer los donantes.
            donor_contract = st.text_input("Ver donantes del contrato:", placeholder="0x...", key="view_donors")
            # Este botón solo hace lectura del contrato (no envía transacción).
            if st.button("Cargar lista"):
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

    col_a, col_b = st.columns(2)
    with col_a:
        # Lista de receptores separada por comas.
        recipients = st.text_area("Recipients (comas)", placeholder="0x1..., 0x2...", height=100)
    with col_b:
        # Lista de cantidades (en unidades humanas) separada por comas.
        amounts = st.text_area("Amounts (unidades)", placeholder="100, 200", height=100)

    st.warning("Asegúrate de aprobar el contrato de airdrop antes de enviar.")

    # Botón 1: aprueba que el contrato de airdrop pueda mover tokens del usuario.
    if st.button("1. Aprobar airdrop"):
        if not token_address or not airdrop_contract:
            st.error("Faltan direcciones.")
        else:
            try:
                with st.spinner("Aprobando..."):
                    # Aprobamos una cantidad muy grande por simplicidad en el TFG
                    # Llamada backend: approve_airdrop() envía transacción al token.
                    tx = w3_manager.approve_airdrop(token_address, airdrop_contract, 10**24)
                    st.success(f"Aprobación enviada: {tx}")
            except Exception as e:
                st.error(f"Error: {e}")

    # Botón 2: ejecuta el airdrop en cadena con receptores y montos.
    if st.button("2. Enviar airdrop"):
        if not airdrop_contract or not token_address or not recipients or not amounts:
            st.error("Rellena todos los campos.")
        else:
            try:
                # Limpieza simple de texto para convertir inputs en listas utilizables.
                rcp_list = [r.strip() for r in recipients.split(",") if r.strip()]
                # Convertimos a unidades con 18 decimales
                amt_list = [int(a.strip()) * 10**18 for a in amounts.split(",") if a.strip()]

                with st.spinner("Enviando Airdrop..."):
                    # Llamada backend: send_airdrop() firma y envía la transacción del contrato.
                    tx = w3_manager.send_airdrop(airdrop_contract, token_address, rcp_list, amt_list)
                    st.success(f"Airdrop ejecutado con éxito")
                    st.code(f"TX Hash: {tx}")
                    st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

with tab3:
    # TAB 3: despliegue de contratos inteligentes desde la misma interfaz.
    st.markdown("<div class='section-title'>Deploy de Contratos</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-helper'>Publica contratos directamente desde la interfaz usando tu configuración Web3.</div>", unsafe_allow_html=True)
    st.markdown("### Lanzar contratos inteligentes")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 1. Cosa Token")
        # Botón de despliegue del contrato de token.
        if st.button("Lanzar token"):
            try:
                with st.spinner("Desplegando Token..."):
                    # Llamada backend: deploy_contract('CosaToken') publica el contrato.
                    res = w3_manager.deploy_contract('CosaToken')
                    st.success(f"Token en: `{res['address']}`")
                    st.code(res['address'])
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        st.markdown("#### 2. Airdrop Contract")
        # Botón de despliegue del contrato de airdrop.
        if st.button("Lanzar airdrop"):
            try:
                with st.spinner("Desplegando Airdrop..."):
                    # Llamada backend: deploy_contract('Airdrop') publica el contrato.
                    res = w3_manager.deploy_contract('Airdrop')
                    st.success(f"Airdrop en: `{res['address']}`")
                    st.code(res['address'])
            except Exception as e:
                st.error(f"Error: {e}")
