import streamlit as st
import time
from web3_utils import Web3Manager
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="TSender", page_icon="🚀", layout="centered")

# --- Custom CSS for the aesthetic ---
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 0%, rgba(30, 27, 75, 0.4) 0%, transparent 50%);
        color: white;
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid rgba(75, 85, 99, 0.4);
        margin-bottom: 2rem;
    }
    .logo-text {
        font-size: 1.25rem;
        font-weight: bold;
        background: -webkit-linear-gradient(left, #ffffff, #9ca3af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .nav-links {
        display: flex;
        gap: 1.5rem;
        font-size: 0.875rem;
        color: #d1d5db;
        font-weight: 500;
    }
    .connect-btn {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: bold;
    }
    .main-card {
        background-color: rgba(17, 24, 39, 0.5);
        backdrop-filter: blur(8px);
        border: 1px solid #1f2937;
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1.5rem;
        margin-top: 2rem;
    }
    .gradient-text {
        font-size: 2.25rem;
        font-weight: bold;
        background: -webkit-linear-gradient(left, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .subtitle {
        color: #9ca3af;
        font-size: 1.125rem;
    }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: transparent !important;
        color: white !important;
        border: 1px solid #374151 !important;
        border-radius: 0.5rem !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 1px #818cf8 !important;
    }
    div.stButton > button:first-child {
        background-color: #4f46e5;
        color: white;
        font-weight: bold;
        border: none;
        width: 100%;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        transition: background-color 0.2s;
        margin-top: 1rem;
    }
    div.stButton > button:first-child:hover {
        background-color: #4338ca;
        color: white;
    }
    .stTextInput label, .stTextArea label {
        color: #e5e7eb !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Siderbar: Configuración Web3 ---
with st.sidebar:
    st.header("⚙️ Configuración Web3")
    st.info("Dado que esto es Python puro vamos a inyectar la URL del nodo (RPC) y la Private Key directamente.")
    
    rpc_url = st.text_input("RPC URL", value=os.getenv("RPC_URL", "https://rpc.sepolia.org"))
    private_key = st.text_input("Private Key", type="password", value=os.getenv("PRIVATE_KEY", ""))
    
    # Instance Web3Manager
    w3_manager = Web3Manager(rpc_url, private_key)
    
    st.divider()
    if w3_manager.is_connected():
        st.success("🟢 Conectado al nodo Blockchain")
        if w3_manager.get_address():
            st.write(f"**Billetera:**")
            st.code(w3_manager.get_address())
            st.write(f"**Balance:** {float(w3_manager.get_balance()):.4f} ETH")
        else:
            st.info("ℹ️ Introduce tu Private Key.")
    else:
        st.error("🔴 No conectado.")

# --- Header ---
wallet_text = f"{w3_manager.get_address()[:6]}...{w3_manager.get_address()[-4:]}" if w3_manager.get_address() else "Esperando billetera..."

st.markdown(f"""
<div class="header-container">
    <div style="display: flex; gap: 2rem; align-items: center;">
        <span class="logo-text">TSender</span>
        <div class="nav-links">
            <span>Inicio</span>
            <span>TFG Project</span>
        </div>
    </div>
    <div>
        <div class="connect-btn">{wallet_text}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Main container ---
st.markdown("""
<div class="main-card">
    <div class="gradient-text">Bienvenido a TSender</div>
    <div class="subtitle">Gestiona tus tokens y airdrops de forma premium.</div>
</div>
""", unsafe_allow_html=True)

# --- Tabs Navigation ---
tab1, tab2, tab3 = st.tabs(["💰 Dashboard Principal", "🚀 Enviar Airdrop", "💎 Lanzar Contratos"])

with tab1:
    st.markdown("### 📊 Tu Balance y Estado")
    if w3_manager.get_address():
        col_main1, col_main2 = st.columns(2)
        with col_main1:
            st.info(f"**Billetera Configurada:**\n`{w3_manager.get_address()}`")
            st.success(f"**Tus Fondos:** {float(w3_manager.get_balance()):.4f} ETH")
        
        with col_main2:
            contract_to_check = st.text_input("Dirección del Contrato (Airdrop/Donación)", placeholder="0x...", key="check_balance")
            if contract_to_check:
                try:
                    c_balance = w3_manager.get_contract_eth_balance(contract_to_check)
                    st.metric("Balance del Contrato", f"{float(c_balance):.4f} ETH")
                except:
                    st.error("Dirección no válida")

        st.divider()
        
        # --- SECCIÓN DE DONACIONES ---
        st.markdown("#### 💌 Realizar Donación al Contrato")
        col_don1, col_don2 = st.columns([2, 1])
        with col_don1:
            target_contract = st.text_input("Dirección Contrato Destino", placeholder="0x...", key="donate_addr")
            donation_amount = st.number_input("Cantidad a donar (ETH)", min_value=0.0001, format="%.4f")
        with col_don2:
            st.write("") # Espaciador
            if st.button("💎 Donar Ahora"):
                if target_contract:
                    try:
                        with st.spinner("Procesando donación..."):
                            tx = w3_manager.donate_eth(target_contract, donation_amount)
                            st.success(f"¡Donación exitosa! TX: {tx[:10]}...")
                            st.balloons()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Pon la dirección del contrato.")

        st.divider()

        # --- SECCIÓN DE LISTA DE DONANTES ---
        st.markdown("#### 👥 Libro de Donantes")
        donor_contract = st.text_input("Ver donantes del contrato:", placeholder="0x...", key="view_donors")
        if st.button("🔍 Cargar Lista"):
            if donor_contract:
                try:
                    donors = w3_manager.get_donors_list(donor_contract)
                    if donors:
                        for d in donors:
                            st.code(d)
                    else:
                        st.info("Aún no hay donantes registrados en este contrato.")
                except Exception as e:
                    st.error(f"No se pudo cargar la lista: {e}")
    else:
        st.error("Conecta tu billetera en el menú lateral para ver tu balance y opciones.")

with tab2:
    st.markdown("### 💸 Realizar Airdrop")
    
    airdrop_contract = st.text_input("Airdrop Contract Address", placeholder="0x... (Despliégalo en la pestaña 3)")
    token_address = st.text_input("Token Address", placeholder="0x...")
    
    col_a, col_b = st.columns(2)
    with col_a:
        recipients = st.text_area("Recipients (comas)", placeholder="0x1..., 0x2...", height=100)
    with col_b:
        amounts = st.text_area("Amounts (unidades)", placeholder="100, 200", height=100)

    st.warning("⚠️ Asegúrate de Aprobar el contrato de Airdrop antes de enviar.")
    
    if st.button("1. ✅ Aprobar Airdrop"):
        if not token_address or not airdrop_contract:
            st.error("Faltan direcciones.")
        else:
            try:
                with st.spinner("Aprobando..."):
                    # Aprobamos una cantidad muy grande por simplicidad en el TFG
                    tx = w3_manager.approve_airdrop(token_address, airdrop_contract, 10**24)
                    st.success(f"Aprobación enviada: {tx}")
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("2. 🚀 Enviar Airdrop"):
        if not airdrop_contract or not token_address or not recipients or not amounts:
            st.error("Rellena todos los campos.")
        else:
            try:
                rcp_list = [r.strip() for r in recipients.split(",") if r.strip()]
                # Convertimos a unidades con 18 decimales
                amt_list = [int(a.strip()) * 10**18 for a in amounts.split(",") if a.strip()]
                
                with st.spinner("Enviando Airdrop..."):
                    tx = w3_manager.send_airdrop(airdrop_contract, token_address, rcp_list, amt_list)
                    st.success(f"✅ Airdrop ejecutado con éxito!")
                    st.code(f"TX Hash: {tx}")
                    st.balloons()
            except Exception as e:
                st.error(f"Error: {e}")

with tab3:
    st.markdown("### 💎 Lanzar Contratos Inteligentes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 1. Cosa Token")
        if st.button("🚀 Lanzar Token"):
            try:
                with st.spinner("Desplegando Token..."):
                    res = w3_manager.deploy_contract('CosaToken')
                    st.success(f"Token en: `{res['address']}`")
                    st.code(res['address'])
            except Exception as e:
                st.error(f"Error: {e}")

    with col2:
        st.markdown("#### 2. Airdrop Contract")
        if st.button("🚀 Lanzar Airdrop"):
            try:
                with st.spinner("Desplegando Airdrop..."):
                    res = w3_manager.deploy_contract('Airdrop')
                    st.success(f"Airdrop en: `{res['address']}`")
                    st.code(res['address'])
            except Exception as e:
                st.error(f"Error: {e}")
