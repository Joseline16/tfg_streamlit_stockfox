
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import psycopg2
from database.conexion import get_connection
from datetime import datetime, timedelta


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

#Obtener categorías unicas
def obtener_categorias():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]


#Nombres de productos por categoria 
def obtener_productos_por_categoria(categoria):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_producto, nombre_producto
        FROM productos
        WHERE categoria = %s
        ORDER BY nombre_producto;
    """, (categoria,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(rows, columns=["id_producto", "nombre_producto"])
    return df


#Ventas mensuales por proucto de categoria
def obtener_ventas_mensuales(categoria):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            v.id_producto,
            DATE_TRUNC('month', v.fecha_venta) AS mes,
            SUM(v.cantidad) AS total_vendido
        FROM ventas v
        JOIN productos p ON v.id_producto = p.id_producto
        WHERE p.categoria = %s
        GROUP BY v.id_producto, mes
        ORDER BY v.id_producto, mes;
    """, (categoria,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(rows, columns=[
        "id_producto", "mes", "total_vendido"
    ])
    return df

#Predicciones a 3 meses 
def generar_predicciones(df_ventas):
    predicciones = []

    productos = df_ventas["id_producto"].unique()

    for prod in productos:
        df_prod = df_ventas[df_ventas["id_producto"] == prod].copy()

        if df_prod.empty or len(df_prod) < 2:
            continue

        df_prod = df_prod.sort_values("mes")
        df_prod["t"] = np.arange(1, len(df_prod) + 1)

        X = df_prod[["t"]]
        y = df_prod["total_vendido"]

        modelo = RandomForestRegressor(n_estimators=200)
        modelo.fit(X, y)

        ult_t = df_prod["t"].max()
        futuros = np.array([ult_t + 1, ult_t + 2, ult_t + 3]).reshape(-1, 1)
        predicciones_y = modelo.predict(futuros)

        ult_fecha = df_prod["mes"].max()
        fechas_futuras = [
            ult_fecha + pd.DateOffset(months=i)
            for i in range(1, 4)
        ]

        for f, p in zip(fechas_futuras, predicciones_y):
            predicciones.append({
                "id_producto": prod,
                "fecha_prediccion": f.date(),
                "demanda_estimada": int(p)
            })

    return pd.DataFrame(predicciones)


#Guardar predicciones en la base de datos predicciones cada que se de en el boton 
def guardar_predicciones(df_pred):
    conn = get_connection()
    cur = conn.cursor()

    for _, row in df_pred.iterrows():
        cur.execute("""
            INSERT INTO prediccion (id_producto, fecha_prediccion, demanda_estimada)
            VALUES (%s, %s, %s)
        """, (row["id_producto"], row["fecha_prediccion"], row["demanda_estimada"]))

    conn.commit()
    cur.close()
    conn.close()


#Parte visual 

st.title("🔮 Predicciones de Demanda Mensual")
st.write("Genera predicciones basadas en ventas históricas por **categoría de producto**.")


# Seleccionar categoría
categorias = obtener_categorias()
categoria_seleccionada = st.selectbox("Selecciona una categoría", categorias)

if categoria_seleccionada:

    st.subheader(f"📦 Categoría seleccionada: **{categoria_seleccionada}**")

    # Obtener ventas mensuales
    df_ventas = obtener_ventas_mensuales(categoria_seleccionada)

    if df_ventas.empty:
        st.warning("No hay ventas registradas para esta categoría.")
        st.stop()

    # Botón para generar predicciones manualmente
    if st.button("🔮 Generar predicciones (3 meses)"):
        df_pred = generar_predicciones(df_ventas)

        if df_pred.empty:
            st.error("No hay suficientes datos históricos para generar predicciones.")
            st.stop()

        # Mostrar predicciones por producto
        st.subheader("📊 Predicciones por producto")
        st.dataframe(df_pred)

        # Resumen por categoría
        st.subheader("📦 Resumen total por categoría")
        df_resumen = df_pred.groupby("fecha_prediccion")["demanda_estimada"].sum().reset_index()
        st.dataframe(df_resumen)

        # Botón para guardar en BD
        if st.button("💾 Guardar predicciones en la base de datos"):
            guardar_predicciones(df_pred)
            st.success("Predicciones guardadas exitosamente.")


