import streamlit as st
import pandas as pd
from baseDatos.conexion import get_connection

st.set_page_config(page_title="Predicciones", layout="wide")


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

st.title("📈 Gestión de Predicciones de Demanda")


# --- Obtener productos ---
def obtener_productos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id_producto, nombre_producto FROM productos;")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return productos

# --- Insertar nueva predicción ---
def insertar_prediccion(id_producto, fecha, demanda):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prediccion (id_producto, fecha_prediccion, demanda_estimada)
        VALUES (%s, %s, %s);
    """, (id_producto, fecha, demanda))
    conn.commit()
    cur.close()
    conn.close()

# --- Obtener lista de predicciones ---
def obtener_predicciones():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id_prediccion,
               pr.nombre_producto AS producto,
               p.fecha_prediccion,
               p.demanda_estimada,
               p.fecha_creacion
        FROM prediccion p
        JOIN productos pr ON p.id_producto = pr.id_producto
        ORDER BY p.fecha_creacion DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# --- UI principal ---
productos = obtener_productos()
productos_dict = {p[1]: p[0] for p in productos}

st.subheader("➕ Registrar nueva predicción")

with st.form("form_prediccion"):
    producto = st.selectbox("Producto", list(productos_dict.keys()))
    fecha_pred = st.date_input("Fecha de predicción")
    demanda = st.number_input("Demanda estimada", min_value=0, step=1)

    submit = st.form_submit_button("Guardar Predicción")

    if submit:
        insertar_prediccion(productos_dict[producto], fecha_pred, demanda)
        st.success("Predicción registrada correctamente.")

# --- Mostrar predicciones ---
st.subheader("📋 Predicciones registradas")

preds = obtener_predicciones()
df = pd.DataFrame(preds, columns=["ID", "Producto", "Fecha Predicción", "Demanda Estimada", "Creado"])

st.dataframe(df, use_container_width=True)