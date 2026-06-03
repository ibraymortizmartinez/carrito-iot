# 🤖 S.T.A.R.K. Rover OS - IoT Car con ESP8266

Este proyecto consiste en un vehículo robótico móvil (**ESP8266 WiFi Robot Car**) controlado de forma inalámbrica a través de un ecosistema IoT distribuido. La arquitectura del sistema separa las responsabilidades en dos aplicaciones web independientes con una interfaz de usuario futurista inspirada en el HUD de **Iron Man (J.A.R.V.I.S. / F.R.I.D.A.Y.)**, comunicadas en tiempo real mediante WebSockets y una API REST construida en Flask.

---

## 🌌 Características Principales

### 🎮 1. Aplicación Web de Pilotaje (`control.html`)
* **Matriz Cinemática de 11 Movimientos:** Permite el desplazamiento en todas las direcciones cardinales, diagonales (avanzar/retroceder izquierdo/derecho), pivotes sobre su propio eje y un freno de emergencia central (*Arc Reactor Stop*).
* **Control de Modulación por Ancho de Pulsos (PWM):** Deslizador responsivo para regular la potencia de tracción de los motores de 0 a 255 RPM.
* **Modo Secuencial DEMO:** Activación de rutas automatizadas preprogramadas desde la interfaz web.

### 📊 2. Aplicación Web de Telemetría (`monitor.html`)
* **Escaner de Radar Activo:** Renderiza la distancia calculada por el sensor de proximidad en tiempo real.
* **Auditoría de Datos:** Despliega de forma estricta los **últimos 5 estados del dispositivo** (maniobras ejecutadas u obstáculos registrados en la base de datos SQL).
* **Alertas Visuales Críticas:** Cambio dinámico del HUD a modo de alerta roja ante colisiones inminentes.

### 🛡️ 3. Sistema de Evasión Autónoma de Obstáculos (Firmware Arduino)
* **Monitoreo Ultrasónico Continuo:** Filtro de calibración inteligente que ignora lecturas falsas (0 cm) y detecta amenazas reales a menos de 20 cm.
* **Maniobra de Pánico Evasiva:** Ante un obstáculo frontal, el vehículo detiene los motores, retrocede para ganar espacio, ejecuta un giro diferencial alternado (derecha/izquierda) para buscar una salida limpia, y retoma de forma automática la última orden del historial enviada desde la web.

---

## 📁 Estructura del Proyecto Web

```text
esp8266-ironman-panel/
│
├── control.html                # APP 1: Interfaz de Pilotaje Remoto
├── monitor.html                # APP 2: HUD de Telemetría y Diagnóstico
├── README.md                   # Documentación General del Proyecto
│
└── assets/
    ├── css/
    │   └── styles.css          # Estilos HUD Stark, Neón y Animaciones
    └── js/
        ├── control.js          # Orquestador de Transmisión de Comandos (WebSockets)
        └── monitor.js          # Receptor del Radar e Historial de Estados