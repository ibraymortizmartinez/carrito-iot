import mysql.connector

class DatabaseModel:
    def __init__(self, host, user, password, database):
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def obtener_ultimo_movimiento(self):
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True) 
        try:
            cursor.callproc('sp_obtener_ultimo_movimiento')
            for result in cursor.stored_results():
                row = result.fetchone()
                if row:
                    row['fecha_hora'] = str(row['fecha_hora'])
                    return row
            return None
        finally:
            cursor.close()
            conn.close()

    def actualizar_parametro(self, clave, valor):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc('sp_actualizar_parametro', (clave, valor))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error actualizando parámetro: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def registrar_movimiento(self, id_movimiento, id_dispositivo, origen):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc('sp_registrar_movimiento', (id_movimiento, id_dispositivo, origen))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error registrando movimiento: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def registrar_obstaculo(self, id_dispositivo, estatus, distancia):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc('sp_registrar_obstaculo', (id_dispositivo, estatus, distancia))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error al registrar obstáculo: {e}")
            return False
        finally:
            cursor.close()
            conn.close()