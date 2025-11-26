from baseDatos.conexion import get_connection
import psycopg2.extras

def verificar_credenciales(email, password):
    conn = get_connection()
    if not conn:
        return False, "No se pudo conectar a la base de datos."

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT id_usuario, nombre_usuario, rol
            FROM usuarios
            WHERE email=%s AND password=%s
        """
        cur.execute(query, (email, password))
        result = cur.fetchone()

        cur.close()
        conn.close()

        if result:
            return True, {
                "id_usuario": result["id_usuario"],
                "nombre_usuario": result["nombre_usuario"],
                "rol": result["rol"]
            }
        else:
            return False, "Usuario o contraseña incorrectos"

    except Exception as e:
        return False, f"Error interno: {e}"