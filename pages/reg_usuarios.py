import streamlit as st
import pandas as pd
import psycopg2
from database.conexion import get_connection

st.set_page_config(layout="wide") 


# Ocultar navegación
st.markdown("""
<style>
[data-testid="stSidebarNav"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

rol = st.session_state.get("rol", "")

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

# Seguridad
if "rol" not in st.session_state:
    st.error("No has iniciado sesión.")
    st.stop()

if st.session_state["rol"] != "administrador":
    st.error("No tienes permisos para ver esta página.")
    st.stop()

#Consilta de usuarios 
def obtener_usuarios(offset, limit, filtro_campo=None, filtro_valor=None, orden="ASC"):

    CAMPOS_VALIDOS = ["nombre_usuario", "email", "rol", "telefono"]
    if filtro_campo not in CAMPOS_VALIDOS:
        filtro_campo = "nombre_usuario"

    try:
        conn = get_connection()
        with conn, conn.cursor() as cur:

            query = """
                SELECT id_usuario, nombre_usuario, email, rol, 
                       id_telegram, telefono, password, fecha_registro
                FROM usuarios
            """

            params = []

            # FILTRO AUTOMÁTICO
            if filtro_valor:
                query += f" WHERE {filtro_campo} ILIKE %s "
                params.append(f"%{filtro_valor}%")

            # ORDEN
            query += f" ORDER BY {filtro_campo} {orden}"

            # PAGINADO
            query += " LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            cur.execute(query, params)
            rows = cur.fetchall()

        columnas = [
            "id_usuario", "nombre_usuario", "email", "rol",
            "id_telegram", "telefono", "password", "fecha_registro"
        ]

        return pd.DataFrame(rows, columns=columnas)

    except Exception as e:
        st.error(f"Error al obtener usuarios: {e}")
        return pd.DataFrame()


#insertar nuevo usuario
def insertar_usuario(nombre, email, rol, telegram, telefono, password):
    try:
        conn = get_connection()
        with conn, conn.cursor() as cur:

            cur.execute("""
                INSERT INTO usuarios (nombre_usuario, email, rol, id_telegram, telefono, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, email, rol, telegram, telefono, password))

        st.success("Usuario registrado correctamente.")

    except Exception as e:
        st.error(f"Error al registrar usuario: {e}")


#Main
def main():
    st.title("Usuarios")

    st.session_state.setdefault("page", 1)
    st.session_state.setdefault("open_modal", False)

    #  FILTROS AUTOMÁTICOS 
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        filtro_campo = st.selectbox(
            "Filtrar por",
            ["nombre_usuario", "email", "rol", "telefono"],
            index=0
        )

    with col2:
        filtro_valor = st.text_input("Buscar...")

    with col3:
        orden = st.selectbox("Orden", ["ASC", "DESC"])

    st.markdown("---")

    # BOTÓN NUEVO 
    if st.button("Nuevo"):
        st.session_state.open_modal = True

    # - MODAL para nuevo usuario, ventana que aparece
    if st.session_state.open_modal:

        with st.form("nuevo_usuario", border=True):
            st.subheader("Nuevo Usuario")

            nombre = st.text_input("Nombre")
            email = st.text_input("Email")
            rol = st.selectbox("Rol", ["administrador", "empleado"])
            telegram = st.text_input("ID Telegram")
            telefono = st.text_input("Teléfono")
            password = st.text_input("Contraseña", type="password")

            col_g, col_c = st.columns(2)
            guardar = col_g.form_submit_button("Guardar")
            cancelar = col_c.form_submit_button("Cancelar")

            if guardar:
                if not nombre or not email or not password:
                    st.warning("Nombre, Email y Contraseña son obligatorios.")
                else:
                    insertar_usuario(nombre, email, rol, telegram, telefono, password)
                    st.session_state.open_modal = False
                    st.rerun()

            if cancelar:
                st.session_state.open_modal = False
                st.rerun()

        st.stop()

    # tabla
    limit = 10
    offset = (st.session_state.page - 1) * limit

    df = obtener_usuarios(
        offset,
        limit,
        filtro_campo,
        filtro_valor if filtro_valor.strip() != "" else None,
        orden
    )

    if df.empty:
        st.warning("No se encontraron usuarios.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

    # paginacion
    left, _, right = st.columns([1, 3, 1])

    with left:
        if st.button("◀ Anterior", disabled=st.session_state.page <= 1):
            st.session_state.page -= 1
            st.rerun()

    with right:
        if st.button("Siguiente ▶", disabled=len(df) < limit):
            st.session_state.page += 1
            st.rerun()

    st.write(f"Página: {st.session_state.page}")


if __name__ == "__main__":
    main()
