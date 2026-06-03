import socket
import hashlib
import base64
import threading
import struct
import json

class RawWebSocketServer:
    def __init__(self, model, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.model = model
        self.clients = []
        # Crear un socket TCP estándar
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

    def start(self):
        print(f"[*] Servidor WebSocket nativo escuchando en ws://{self.host}:{self.port}")
        threading.Thread(target=self._accept_clients, daemon=True).start()

    def _accept_clients(self):
        while True:
            client, addr = self.server_socket.accept()
            print(f"[+] Nueva conexion TCP establecida desde: {addr}")
            threading.Thread(target=self._handle_client, args=(client, addr), daemon=True).start()

    def _handle_client(self, client, addr):
        try:
            request = client.recv(1024).decode('utf-8', errors='ignore')
            headers = self._parse_headers(request)
            
            # Handshake del WebSocket
            if 'Sec-WebSocket-Key' in headers:
                key = headers['Sec-WebSocket-Key']
                accept_key = self._generate_accept_key(key)
                response = (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
                )
                client.send(response.encode('utf-8'))
                self.clients.append(client)
                print(f"[WS] Handshake exitoso. Cliente {addr} agregado al historial en vivo.")
                
                # Al conectarse, enviamos el estado actual inmediatamente
                self.send_last_movement(client)
                
                # LOOP CRÍTICO REPARADO: Mantiene vivo el socket decodificando tramas estructuradas
                while True:
                    data = client.recv(2048)
                    if not data:
                        break  # El cliente cerró la conexión
                    
                    # Decodificar el marco WebSocket enmascarado del navegador
                    decoded_text = self._decode_message(data)
                    if decoded_text:
                        print(f"[WS RECEIVE] Comando decodificado de {addr}: {decoded_text}")
                        # Retransmitir la instrucción recibida en ráfaga (Hacia el coche u otros paneles)
                        self.broadcast(decoded_text)
                        
        except Exception as e:
            print(f"[-] Conexion perdida con el cliente {addr}: {e}")
        finally:
            if client in self.clients:
                self.clients.remove(client)
            client.close()
            print(f"[-] Cliente {addr} eliminado de la lista activa.")

    def _parse_headers(self, request):
        headers = {}
        lines = request.split('\r\n')
        for line in lines[1:]:
            if ': ' in line:
                k, v = line.split(': ', 1)
                headers[k] = v
        return headers

    def _generate_accept_key(self, key):
        magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        return base64.b64encode(hashlib.sha1((key + magic).encode('utf-8')).digest()).decode('utf-8')

    def _decode_message(self, data):
        """ Desenmarca y decodifica tramas estándar RFC 6455 enviadas por los navegadores """
        try:
            if len(data) < 6:
                return None
                
            second_byte = data[1]
            has_mask = (second_byte & 0x80) != 0
            payload_length = second_byte & 0x7F
            
            idx = 2
            if payload_length == 126:
                payload_length = struct.unpack(">H", data[2:4])[0]
                idx = 4
            elif payload_length == 127:
                payload_length = struct.unpack(">Q", data[2:10])[0]
                idx = 10
                
            if not has_mask:
                return data[idx:idx+payload_length].decode('utf-8', errors='ignore')
                
            mask_key = data[idx:idx+4]
            idx += 4
            
            payload = data[idx:idx+payload_length]
            unmasked_bytes = bytearray(b ^ mask_key[i % 4] for i, b in enumerate(payload))
            
            return unmasked_bytes.decode('utf-8', errors='ignore')
        except:
            return None

    def _send_message(self, client, message):
        msg_bytes = message.encode('utf-8')
        header = bytearray([0x81]) # 0x81 indica texto
        length = len(msg_bytes)
        
        if length <= 125:
            header.append(length)
        elif length >= 126 and length <= 65535:
            header.append(126)
            header.extend(struct.pack(">H", length))
        else:
            header.append(127)
            header.extend(struct.pack(">Q", length))
            
        try:
            client.send(header + msg_bytes)
        except:
            if client in self.clients:
                self.clients.remove(client)

    def broadcast(self, message):
        print(f"[WS] Enviando ráfaga (Broadcast) a {len(self.clients)} clientes conectados.")
        for client in list(self.clients):
            self._send_message(client, message)

    def send_last_movement(self, target_client=None):
        data = self.model.obtener_ultimo_movimiento()
        if data:
            json_msg = json.dumps(data)
            if target_client:
                self._send_message(target_client, json_msg)
            else:
                self.broadcast(json_msg)