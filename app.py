import streamlit as st
from services.auxiliares import verificar_credenciales

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="StockFox", page_icon="🦊")

#Ocultamos el sidebar 
if "logueado" not in st.session_state or not st.session_state["logueado"]:
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
        .block-container {padding-left: 2rem !important;}
    </style>
    """, unsafe_allow_html=True)

# Ocultamos navegación automática de Streamlit
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


# Forzamos el cambio de color de los Inputs a blancos
st.markdown(""" 
<style>
.stTextInput > div > div > input {
    background-color: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

load_css("style.css")

# ---------------------
# FORMULARIO DE LOGIN
# ---------------------
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    with st.form("login_form"):
        st.title("StockFox")
        st.subheader("Iniciar Sesión")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        btn = st.form_submit_button("Sign In")


# ---------------------
# PROCESAR LOGIN
# ---------------------
if btn:
    ok, data = verificar_credenciales(email, password)
    if ok:
        st.session_state["usuario"] = data
        st.session_state["logueado"] = True
        st.session_state["rol"] = data["rol"]
        st.session_state["id_usuario"] = data["id_usuario"]
        st.session_state["mensaje_bienvenida"] = f"Bienvenido, {data['nombre_usuario']}!"

        st.success(st.session_state["mensaje_bienvenida"])

        st.switch_page("pages/pagina_principal.py")
    else:
        st.error(data)

