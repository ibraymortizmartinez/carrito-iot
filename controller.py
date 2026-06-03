import json
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS # Requiere instalación: pip install flask-cors

class APIController:
    def __init__(self, model, ws_server):
        self.app = Flask(__name__)
        
        # Habilitación de orígenes cruzados para evitar bloqueos por IP local
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        
        self.model = model
        self.ws_server = ws_server
        
        # Mutex Lock para evitar colisiones críticas de red entre hilos
        self.network_lock = threading.Lock()
        self._setup_routes()

    def _safe_ws_broadcast(self, msg_json):
        """ Envía mensajes al socket asegurando sincronía entre hilos """
        with self.network_lock:
            try:
                self.ws_server.broadcast(msg_json)
            except Exception as e:
                print(f"[WS THREAD ERROR] No se pudo esparcir la ráfaga: {e}")

    def _safe_ws_last_movement(self):
        """ Actualiza el último estado de movimiento de manera síncrona """
        with self.network_lock:
            try:
                self.ws_server.send_last_movement()
            except Exception as e:
                print(f"[WS THREAD ERROR] Error de refresco en vivo: {e}")

    def _setup_routes(self):
        @self.app.route('/api/actualizar_parametro', methods=['POST'])
        def actualizar_parametro():
            data = request.get_json()
            clave = data.get('clave')
            valor = data.get('valor')
            
            if self.model.actualizar_parametro(clave, valor):
                return jsonify({"status": "success", "message": "Parámetro actualizado"}), 200
            else:
                return jsonify({"status": "error", "message": "Fallo al actualizar"}), 500

        @self.app.route('/api/registrar_movimiento', methods=['POST'])
        def registrar_movimiento():
            data = request.get_json()
            id_mov = data.get('id_movimiento')
            id_disp = data.get('id_dispositivo')
            origen = data.get('origen')
            
            if self.model.registrar_movimiento(id_mov, id_disp, origen):
                self._safe_ws_last_movement()
                return jsonify({"status": "success", "message": "Movimiento registrado"}), 200
            else:
                return jsonify({"status": "error", "message": "Fallo al registrar"}), 500

        @self.app.route('/api/obtener_ultimo_movimiento', methods=['GET'])
        def obtener_ultimo_movimiento():
            data = self.model.obtener_ultimo_movimiento()
            if data:
                return jsonify(data), 200
            return jsonify({"status": "error", "message": "Sin datos"}), 404

        @self.app.route('/api/registrar_obstaculo', methods=['POST'])
        def registrar_obstaculo():
            data = request.get_json()
            id_disp = data.get('id_dispositivo')
            distancia = data.get('distancia')
            
            if id_disp is None or distancia is None:
                return jsonify({"status": "error", "message": "Datos incompletos"}), 400
                
            distancia_flotante = float(distancia)
            estatus = "OBSTACULO" if distancia_flotante < 20.0 else "LIBRE"
            
            if self.model.registrar_obstaculo(id_disp, estatus, distancia):
                evento_sensor = {
                    "evento": "lectura_sensor",
                    "id_dispositivo": id_disp,
                    "estatus": estatus,
                    "distancia": distancia_flotante
                }
                self._safe_ws_broadcast(json.dumps(evento_sensor))
                
                # --- SISTEMA DE LOGICA AUTÓNOMA ---
                if estatus == "OBSTACULO":
                    print(f"[ALERTA AUTÓNOMA] Obstáculo a {distancia_flotante}cm! Frenando...")
                    
                    id_detener = 3 
                    if self.model.registrar_movimiento(id_detener, id_disp, 'AUTONOMO_EVASION'):
                        self._safe_ws_last_movement()
                        
                    import time
                    time.sleep(0.5) # Breve ventana de tiempo física para el frenado mecánico
                    
                    id_girar = 8 
                    print("[ALERTA AUTÓNOMA] Evadiendo ruta: Girando 90° a la derecha.")
                    if self.model.registrar_movimiento(id_girar, id_disp, 'AUTONOMO_EVASION'):
                        self._safe_ws_last_movement()
                
                return jsonify({"status": "success", "message": "Obstáculo procesado"}), 200
            else:
                return jsonify({"status": "error", "message": "Fallo al registrar en BD"}), 500

    def run(self):
        print("[*] Servidor Flask API iniciado en http://0.0.0.0:5000")
        self.app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)