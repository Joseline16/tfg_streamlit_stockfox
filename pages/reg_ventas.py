import streamlit as st
import pandas as pd
from datetime import date
from database.conexion import get_connection

if "id_usuario" not in st.session_state:
    st.error("Error interno: falta id_usuario en la sesión.")
    st.stop()

    
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



#Obtener las ventas
def obtener_ventas(f_inicio=None, f_fin=None, codigo=None, producto=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT 
        v.id_venta,
        v.codigo_venta,
        v.cantidad,
        v.precio_unitario,
        v.total,
        v.fecha_venta,
        v.id_producto,
        p.nombre_producto,
        p.marca
    FROM ventas v
    JOIN productos p ON v.id_producto = p.id_producto
    WHERE 1=1
    """

    params = []

    if f_inicio:
        query += " AND v.fecha_venta >= %s"
        params.append(f_inicio)

    if f_fin:
        query += " AND v.fecha_venta <= %s"
        params.append(f_fin)

    if codigo:
        query += " AND v.codigo_venta LIKE %s"
        params.append(f"%{codigo}%")

    if producto:
        query += " AND p.nombre_producto LIKE %s"
        params.append(f"%{producto}%")

    cur.execute(query, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]

    cur.close()
    conn.close()

    return pd.DataFrame(rows, columns=cols)


#Registrar una venta
def registrar_venta(id_usuario, codigo_venta, id_producto, cantidad, fecha_venta):
    conn = get_connection()
    try:
        cur = conn.cursor()

        query = """
        INSERT INTO ventas (id_usuario, codigo_venta, id_producto, cantidad, fecha_venta)
        VALUES (%s, %s, %s, %s, %s)
        """

        cur.execute(query, (id_usuario, codigo_venta, id_producto, cantidad, fecha_venta))

        conn.commit()
        cur.close()
        conn.close()

        return True

    except Exception as e:
        return f"Error al registrar venta: {e}"


#Ventana emergente de registro de venta
@st.dialog("Registrar nueva venta")
def modal_registrar_venta():

    id_usuario = st.session_state.get("id_usuario", None)

    if not id_usuario:
        st.error("❌ No se encontró id_usuario en la sesión.")
        return

    st.write("Complete los datos de la venta:")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_producto, nombre_producto, marca, categoria, precio_unitario
        FROM productos
        ORDER BY marca, nombre_producto
    """)
    productos = cur.fetchall()
    cur.close()
    conn.close()

    marcas = sorted(list(set([p[2] for p in productos])))

    marca_sel = st.selectbox("Marca", marcas)

    productos_filtrados = [p for p in productos if p[2] == marca_sel]

    prod_dict = {
        f"{p[1]}": {
            "id": p[0],
            "nombre": p[1],
            "categoria": p[3],
            "precio": p[4]
        }
        for p in productos_filtrados
    }

    producto_sel = st.selectbox("Producto", list(prod_dict.keys()))

    info = prod_dict[producto_sel]

    st.info(f"🆔 **ID del producto:** {info['id']}")
    st.info(f"🏷 **Categoría:** {info['categoria']}")
    st.info(f"💲 **Precio unitario:** S/ {info['precio']}")

    codigo_venta = st.text_input("Código de venta")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    fecha_venta = st.date_input("Fecha de venta", value=date.today())

    if st.button("Registrar"):
        r = registrar_venta(
            id_usuario=id_usuario,
            codigo_venta=codigo_venta,
            id_producto=info["id"],
            cantidad=cantidad,
            fecha_venta=fecha_venta
        )

        if r is True:
            st.success("Venta registrada correctamente.")
            st.rerun()
        else:
            st.error(r)


st.title("💰 Registro de Ventas")

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

with col1:
    f_inicio = st.date_input("Desde", value=None)

with col2:
    f_fin = st.date_input("Hasta", value=None)

with col3:
    codigo = st.text_input("Código de venta")

with col4:
    producto = st.text_input("Producto")

# --- BOTÓN LIMPIAR ---
if st.button("🔄 Limpiar"):
    for key in list(st.session_state.keys()):
        if key not in ["id_usuario", "rol"]:
            del st.session_state[key]
    st.session_state["pagina_ventas"] = 1
    st.rerun()

# Boton nuevo
if st.button("➕ Nuevo"):
    modal_registrar_venta()

# Obtener ventas
df = obtener_ventas(f_inicio, f_fin, codigo, producto)

#Paginacion 
if "pagina_ventas" not in st.session_state:
    st.session_state.pagina_ventas = 1

filas_por_pagina = 10
total_filas = len(df)
total_paginas = max(1, (total_filas - 1) // filas_por_pagina + 1)

inicio = (st.session_state.pagina_ventas - 1) * filas_por_pagina
fin = inicio + filas_por_pagina

df_pagina = df.iloc[inicio:fin]

#Tabla
st.write(f"### 📋 Lista de ventas registradas (Página {st.session_state.pagina_ventas} / {total_paginas})")
st.dataframe(df_pagina, use_container_width=True, hide_index=True)

#Botones de paginacion
colPrev, colNext = st.columns([1, 1])

with colPrev:
    if st.button("⬅️ Anterior") and st.session_state.pagina_ventas > 1:
        st.session_state.pagina_ventas -= 1
        st.rerun()

with colNext:
    if st.button("Siguiente ➡️") and st.session_state.pagina_ventas < total_paginas:
        st.session_state.pagina_ventas += 1
        st.rerun()
