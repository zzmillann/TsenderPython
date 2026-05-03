# TSender 🚀 - Web3 Airdrop & Management Console

Este proyecto ha sido desarrollado como parte de un **Trabajo de Fin de Grado (TFG)**. Consiste en una aplicación descentralizada (DApp) profesional construida íntegramente en **Python**, diseñada para simplificar la gestión de operaciones en la blockchain de Ethereum (específicamente en la red de pruebas Sepolia).

TSender permite realizar envíos masivos de tokens (Airdrops), desplegar contratos inteligentes ERC-20, gestionar donaciones y analizar estadísticas de red, todo desde una interfaz moderna, fluida y coherente.

---

## 🛠️ Stack Tecnológico

El proyecto destaca por el uso de tecnologías líderes en el ecosistema Python y Blockchain:

### 1. Núcleo y Frameworks
*   **[Python 3.13+]**: Lenguaje principal de toda la lógica de backend y procesamiento.
*   **[Streamlit]**: Framework utilizado para la interfaz de usuario. Permite crear aplicaciones web reactivas y de alto rendimiento directamente en Python.

### 2. Interacción con Blockchain
*   **[Web3.py]**: Librería fundamental para la comunicación con nodos Ethereum a través de protocolos RPC. Se encarga de la firma de transacciones, consulta de balances y ejecución de funciones en Smart Contracts.
*   **[Solidity]**: Lenguaje de programación para los Smart Contracts desplegados (`Airdrop.sol`, `CosaToken.sol`).

### 3. Procesamiento y Análisis de Datos
*   **[Pandas]**: Utilizado para la limpieza, manipulación y normalización de datos procedentes de archivos CSV y bases de datos.
*   **[Plotly]**: Motor de visualización interactiva para generar gráficos estadísticos sobre la actividad de la cuenta.
*   **[SQLite]**: Base de datos relacional ligera integrada (vía `sqlite3`) para mantener un historial local de transacciones persistente.

### 4. Utilidades y Configuración
*   **[Python-dotenv]**: Gestión segura de variables de entorno (claves privadas, URLs RPC).
*   **[Logging]**: Sistema de registro centralizado para auditoría y depuración en tiempo real.

---

## 📂 Estructura del Proyecto

```text
dapp_python/
├── app.py                # Punto de entrada principal (Interfaz Streamlit)
├── web3_utils.py         # Capa de lógica Blockchain y gestión de Web3
├── db.py                 # Gestión de la base de datos SQLite (Historial)
├── logger_config.py      # Configuración del sistema de logs profesional
├── .env                  # Variables sensibles (No incluido en control de versiones)
├── contracts/            # Archivos fuente Solidity (.sol)
├── venv/                 # Entorno virtual de Python
└── historial.db          # Base de datos local autogenerada
```

---

## 🚀 Instalación y Configuración

Siga estos pasos para replicar el entorno de desarrollo:

### 1. Clonar el repositorio
```bash
git clone https://github.com/zzmillann/TsenderPython.git
cd TsenderPython/dapp_python
```

### 2. Configurar el Entorno Virtual
```powershell
# Crear el entorno
python -m venv venv

# Activar en Windows
.\venv\Scripts\activate

# Instalar dependencias
pip install streamlit web3 pandas plotly python-dotenv
```

### 3. Variables de Entorno
    Crea un archivo `.env` en la carpeta `dapp_python/` con el siguiente contenido:
    ```env
    RPC_URL=https://ethereum-sepolia-rpc.publicnode.com
    PRIVATE_KEY= Aqui va la clave secreta de tu wallet 
    ```

---

## 💡 Funcionalidades Principales

### 📤 Airdrop Masivo
Importa listas de destinatarios mediante archivos **CSV** o entrada manual. El sistema valida las direcciones Ethereum en tiempo real y estima el coste de gas antes de ejecutar la transacción.

### 🪙 Gestión de Tokens y Contratos
Despliegue automático de contratos **ERC-20** personalizados (incluyendo la creación de nuestra propia criptomoneda **COSA**) y contratos de **Airdrop**. Incluye visualización directa de balances y permisos (allowances).

### 📊 Dashboard de Estadísticas
Visualización interactiva de la actividad histórica:
*   Total de transacciones enviadas.
*   Ratio de éxito/error.
*   Gráficos de distribución de operaciones.
*   Evolución temporal de la actividad on-chain.

### 🕵️ Auditoría y Transparencia
Integración directa con **Etherscan** para verificar cada transacción y contrato desplegado. Sistema de logs detallado que registra cada evento significativo del sistema.

---

## ⚖️ Licencia y Autor
Este proyecto ha sido diseñado por **Alejandro ,Marcos y Kike** como parte de su TFG. El código se proporciona con fines educativos y de demostración de habilidades en desarrollo **Web3** con **Python**.

> [!IMPORTANT]
> **Seguridad**: Nunca compartas tu `PRIVATE_KEY`. La aplicación la utiliza únicamente para firmar transacciones de forma local.
