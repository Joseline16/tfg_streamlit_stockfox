import streamlit as st

# Ocultar navegación automática de Streamlit
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


# Obtener rol
rol = st.session_state.get("rol", "")

# Sidebar personalizado
with st.sidebar:
    st.markdown("""
        <h2 style='color:#FF6A00;'>🦊 StockFox</h2>
        <hr>
    """, unsafe_allow_html=True)

    st.page_link("pages/pagina_principal.py", label="🏠 Inicio")
    st.page_link("pages/predicciones.py", label="📊 Predicciones")
    st.page_link("pages/reg_productos.py", label="📦 Productos")

    if rol == "administrador":
        st.page_link("pages/reg_usuarios.py", label="👤 Gestión de Usuarios")

    st.page_link("pages/reg_ventas.py", label="💰 Ventas")

    st.write("---")
    st.page_link("app.py", label="🚪 Cerrar Sesión")
