import streamlit as st
import pandas as pd
from database.conexion import get_connection


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

#Obtener productos 
def obtener_productos():
    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    query = """
        SELECT id_producto, nombre_producto, categoria, marca,
               stock_actual, stock_minimo, precio_unitario,estado,
               fecha_creacion
        FROM productos
        WHERE estado = 'activo'
        ORDER BY id_producto ASC
    """

    try:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    
    except Exception as e:
        st.error(f"Error al obtener productos: {e}")
        return pd.DataFrame()



#Insertar nuevos productos 
def insertar_producto(nombre, categoria, marca, stock, stock_min, precio):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
        INSERT INTO productos (nombre_producto, categoria, marca, stock_actual, stock_minimo, precio_unitario)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (nombre, categoria, marca, stock, stock_min, precio))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return f"Error al insertar: {e}"



#Actualizar productos
def actualizar_producto(idp, nombre, categoria, marca, stock, stock_min, precio,estado):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = """
        UPDATE productos 
        SET nombre_producto=%s, categoria=%s, marca=%s,
            stock_actual=%s, stock_minimo=%s, precio_unitario=%s,estado=%s
        WHERE id_producto=%s
        """
        cur.execute(query, (nombre, categoria, marca, stock, stock_min, precio, estado,idp))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return f"Error al actualizar: {e}"


#Eliminar productos
def eliminar_producto(idp):
    conn = get_connection()
    try:
        cur = conn.cursor()
        query = "UPDATE productos SET estado='inactivo' WHERE id_producto=%s"
        cur.execute(query, (idp,))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return f"Error al eliminar: {e}"


# ---------------------------------------------------
# DIALOG: Nuevo producto
# ---------------------------------------------------
@st.dialog("Registrar nuevo producto")
def modal_nuevo_producto():
    st.write("Complete la información del nuevo producto:")

    nombre = st.text_input("Nombre del producto")
    categoria = st.text_input("Categoría")
    marca = st.text_input("Marca")
    stock = st.number_input("Stock actual", 0)
    stock_min = st.number_input("Stock mínimo", 0)
    precio = st.number_input("Precio unitario", 0.0)

    if st.button("Guardar"):
        r = insertar_producto(nombre, categoria, marca, stock, stock_min, precio)
        if r is True:
            st.success("Producto registrado correctamente.")
            st.rerun()
        else:
            st.error(r)


#Ventana modificar producto 
@st.dialog("Modificar producto")
def modal_modificar_producto(row):
    st.write("Actualizar información del producto:")

    nombre = st.text_input("Nombre", row["nombre_producto"])
    categoria = st.text_input("Categoría", row["categoria"])
    marca = st.text_input("Marca", row["marca"])
    stock = st.number_input("Stock actual", value=int(row["stock_actual"]))
    stock_min = st.number_input("Stock mínimo", value=int(row["stock_minimo"]))
    precio = st.number_input("Precio unitario", value=float(row["precio_unitario"]))
    
    estado = st.selectbox(
        "Estado",
        ["activo", "inactivo"],
        index=0 if row["estado"] == "activo" else 1
    )
    if st.button("Actualizar"):
        r = actualizar_producto(row["id_producto"], nombre, categoria, marca, stock, stock_min, precio)
        if r is True:
            st.success("Producto actualizado.")
            st.rerun()
        else:
            st.error(r)

# ---------------------------------------------------
# Main
# ---------------------------------------------------
def main():

    st.title("Gestión de Productos")

    df = obtener_productos()
    if df.empty:
        st.info("No hay productos disponibles.")
        return

#Filtros
    col1, col2 = st.columns(2)

    with col1:
        campo = st.selectbox("Buscar por:", ["nombre_producto", "marca", "categoria"])
    with col2:
        valor = st.text_input("Valor")

    if valor:
        df = df[df[campo].str.contains(valor, case=False, na=False)]

#Ordenar ascendente o descendente 
    opciones = {
        "Nombre A-Z": ("nombre_producto", True),
        "Nombre Z-A": ("nombre_producto", False),
        "Stock ascendente": ("stock_actual", True),
        "Stock descendente": ("stock_actual", False)
    }

    col3, col4 = st.columns(2)
    with col3:
        orden_sel = st.selectbox("Ordenar por:", list(opciones.keys()))

    campo_orden, asc = opciones[orden_sel]
    df = df.sort_values(campo_orden, ascending=asc)

    with col4:
        cantidad = st.selectbox("Mostrar:", [5, 10, 20, 50])

 #Paginacion de productos 
    total = len(df)
    paginas = (total - 1) // cantidad + 1

    if "pagina_prod" not in st.session_state:
        st.session_state.pagina_prod = 1

    colA, colB, colC = st.columns([1,2,1])

    with colA:
        if st.button("⟵ Anterior", disabled=st.session_state.pagina_prod == 1):
            st.session_state.pagina_prod -= 1
            st.rerun()

    with colC:
        if st.button("Siguiente ⟶", disabled=st.session_state.pagina_prod == paginas):
            st.session_state.pagina_prod += 1
            st.rerun()

    with colB:
        st.markdown(f"<h5 style='text-align:center;'>Página {st.session_state.pagina_prod} / {paginas}</h5>", unsafe_allow_html=True)

    ini = (st.session_state.pagina_prod - 1) * cantidad
    fin = ini + cantidad
    df_page = df.iloc[ini:fin]

    # =====================================================
    # seleccionar fila 
    # =====================================================
    st.subheader("Productos")

    selected = st.dataframe(
        df_page,
        use_container_width=True,
        hide_index=True,
        on_select="rerun"
    )

    # Obtiene la row seleccionada
    row = None
    if selected["selection"]["rows"]:
        row_index = selected["selection"]["rows"][0]
        row = df_page.iloc[row_index]

#operaciones crud 
    st.divider()
    col_add, col_edit, col_del = st.columns(3)

    with col_add:
        if st.button("➕ Añadir producto"):
            modal_nuevo_producto()

    with col_edit:
        if st.button("✏️ Modificar", disabled=row is None):
            modal_modificar_producto(row)

    with col_del:
        if st.button("🗑️ Eliminar", disabled=row is None):
            r = eliminar_producto(row["id_producto"])
            if r is True:
                st.success("Producto eliminado.")
                st.rerun()
            else:
                st.error(r)



# Ejecutar
if __name__ == "__main__":
    main()
