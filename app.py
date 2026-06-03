from model import DatabaseModel
from ws_server import RawWebSocketServer
from controller import APIController

if __name__ == '__main__':
    # 1. Instanciamos el Modelo LOCAL 
    # (Usamos los datos exactos de tu pestaña de VS Code)
    db_model = DatabaseModel(
        host="127.0.0.1",       # <-- Tu Host local
        user="root",            # <-- Tu Username
        password="Angel_1509",  # <-- La contraseña que configuraste en tu VS Code
        database="carrito_iot"  # <-- Nombre de tu base de datos local
    )

    # 2. Instanciamos e iniciamos el Servidor WebSocket en puerto 5001 (Hilo secundario)
    ws = RawWebSocketServer(model=db_model, host='0.0.0.0', port=5001)
    ws.start()

    # 3. Instanciamos e iniciamos el Controlador Flask en puerto 5000 (Hilo principal)
    api = APIController(model=db_model, ws_server=ws)
    api.run()