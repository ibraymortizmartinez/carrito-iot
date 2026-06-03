// ============================================================================
// CONFIGURACIÓN DE ENDPOINTS PARA DESPLIEGUE DESDE GITHUB PAGES
// ============================================================================

// Forzamos a que el HUD (aunque esté en GitHub) busque el servidor dentro de tu laptop
const SERVER_IP = "10.54.189.128"; 

const WS_URL = `ws://${SERVER_IP}:5001/`;

let socket;
let demoSequences = []; 
let isRecording = false;

// ============================================================================
// INICIALIZACIÓN Y GESTIÓN DEL ENLACE WEBSOCKET
// ============================================================================
function initWebSocket() {
    console.log(`[SISTEMA] Intentando enlazar canal táctico en: ${WS_URL}`);
    socket = new WebSocket(WS_URL);
    const statusLabel = document.getElementById("ws-status");

    socket.onopen = () => {
        if (statusLabel) {
            statusLabel.innerText = "ONLINE // J.A.R.V.I.S. ENLAZADO";
            statusLabel.className = "text-emerald-400 font-bold drop-shadow-[0_0_5px_#10b981]";
        }
        addLogEntry("SISTEMA", "Canal de comunicación WebSocket establecido con éxito.", "text-emerald-400");
    };

    socket.onclose = () => {
        if (statusLabel) {
            statusLabel.innerText = "OFFLINE // RECONECTANDO";
            statusLabel.className = "text-red-500 font-bold animate-pulse";
        }
        addLogEntry("ALERTA", "Enlace caído. Reintentando acoplamiento en 3 segundos...", "text-red-500 font-bold");
        setTimeout(initWebSocket, 3000); // Reconexión automática cíclica
    };

    socket.onerror = (error) => {
        console.error("[WS ERROR]", error);
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            // Procesamiento Avanzado de Telemetría (Lecturas del sensor ultrasónico del Rover)
            if (data.distancia !== undefined && data.distancia !== null) {
                const distanceEl = document.getElementById("radar-distance");
                const alertEl = document.getElementById("radar-alert");
                const pulse = document.getElementById("radar-pulse");
                
                let dist = parseInt(data.distancia);
                
                // Actualiza el texto central del HUD con los centímetros actuales
                if (distanceEl) {
                    distanceEl.innerText = `${dist} CM`;
                }
                
                // Analizador de proximidad táctica y gestión de alertas visuales en el radar
                if (dist < 20 && dist > 0) {
                    if (alertEl) {
                        alertEl.innerText = "🚨 CORTE DE PROXIMIDAD CRÍTICO";
                        alertEl.className = "text-[9px] text-red-500 font-bold tracking-widest animate-pulse";
                    }
                    if (pulse) {
                        pulse.className = "absolute w-full h-full bg-red-500/20 rounded-full border border-red-500 animate-ping";
                    }
                } else {
                    if (alertEl) {
                        alertEl.innerText = "// TELEMETRÍA EN LÍNEA";
                        alertEl.className = "text-[9px] text-emerald-500 font-bold tracking-widest";
                    }
                    if (pulse) {
                        pulse.className = "absolute w-full h-full bg-cyan-400/10 rounded-full border border-cyan-400/30 animate-ping";
                    }
                }
            }
        } catch (e) {
            console.error("Error parseando WebSocket Data recibido", e);
        }
    };
}

// ============================================================================
// SISTEMA DE CONTROL DE MOVIMIENTO (MODO CRUCERO CONTINUO)
// ============================================================================
function send(direccion) { sendCommand(direccion); }

function sendCommand(direccion) {
    // Captura el valor actual del slider de potencia (0 a 255)
    const speed = parseInt(document.getElementById("speed-range")?.value) || 255;
    
    // Cálculo de velocidad reducida (75%) para optimizar la tracción en curvas
    const speedGiro = Math.round(speed * 0.75);

    // Grabación histórica en memoria si el Modo Secuenciador DEMO está activo
    if (isRecording && direccion !== "STOP") {
        demoSequences.push({ direccion, speed });
        addLogEntry("DEMO_REC", `Paso guardado: ${direccion} a ${speed} PWM`, "text-yellow-400");
    }

    let id_movimiento = 3; // Por defecto 'STOP'
    let MIA = "0", MIB = "0", MDA = "0", MDB = "0";
    let MITime = 0, MDTim = 0; // Forzados a 0 para eliminar bloqueos por delay() en Arduino

    // Procesamiento y homologación de rutas exactas con el index.html
    switch (direccion.toUpperCase()) {
        case "ADELANTE":
            id_movimiento = 1;
            MIA = "0";          MIB = String(speed);
            MDA = String(speed); MDB = "0";
            break;
            
        case "ATRAS":
            id_movimiento = 2;
            MIA = String(speed); MIB = "0";
            MDA = "0";           MDB = String(speed);
            break;

        case "DERECHA": // Giro cerrado sobre su propio eje (Pivote Derecha)
            id_movimiento = 8;
            MIA = "0";           MIB = String(speed);
            MDA = "0";           MDB = String(speed); 
            break;
            
        case "IZQUIERDA": // Giro cerrado sobre su propio eje (Pivote Izquierda)
            id_movimiento = 9; 
            MIA = String(speed); MIB = "0";
            MDA = String(speed); MDB = "0"; 
            break;

        case "DIAG_DA": // Diagonal Delantera Derecha (Vuelta suave)
            id_movimiento = 4;
            MIA = "0";               MIB = String(speed);
            MDA = String(speedGiro); MDB = "0";
            break;

        case "DIAG_IA": // Diagonal Delantera Izquierda (Vuelta suave)
            id_movimiento = 5;
            MIA = String(speedGiro); MIB = "0";
            MDA = String(speed);     MDB = "0";
            break;

        case "DIAG_DR": // Diagonal Trasera Derecha
            id_movimiento = 6;
            MIA = String(speed); MIB = "0";
            MDA = "0";           MDB = String(speedGiro);
            break;

        case "DIAG_IR": // Diagonal Trasera Izquierda
            id_movimiento = 7;
            MIA = String(speedGiro); MIB = "0";
            MDA = "0";           MDB = String(speed);
            break;

        case "STOP":
        default:
            id_movimiento = 3;
            MIA = "0"; MIB = "0"; MDA = "0"; MDB = "0";
            break;
    }

    // Payload empaquetado estructurado para coincidir con tu Backend y la base de datos MySQL
    let payload = {
        id_movimiento: id_movimiento,
        movimiento: direccion,
        MIA: MIA,
        MIB: MIB,
        MDA: MDA,
        MDB: MDB,
        MITime: MITime,
        MDTim: MDTim
    };

    // Envío del paquete de datos a través de la ráfaga WebSocket activa
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify(payload));
        addLogEntry("TRANSMISIÓN", `CMD: ${direccion} (${speed} PWM)`, "text-cyan-400");
    } else {
        addLogEntry("ERROR", "No se pudo transmitir el comando. Canal inactivo.", "text-red-500");
    }
}

// ============================================================================
// LÓGICA DE CONTROL DEL SECUENCIADOR / MODO DEMO
// ============================================================================
function toggleRecording() {
    isRecording = !isRecording;
    const btn = document.getElementById("btn-record");
    if (isRecording) {
        demoSequences = [];
        if(btn) btn.innerText = "🔴 DETENER GRABACIÓN";
        addLogEntry("SISTEMA", "Modo Secuenciador Activado. Registrando movimientos...", "text-yellow-500 font-bold");
    } else {
        if(btn) btn.innerText = "Grabar Ruta Demo";
        addLogEntry("SISTEMA", `Grabación finalizada con éxito. ${demoSequences.length} pasos guardados.`, "text-orange-400");
    }
}

function ejecutarModoDemo() {
    if (demoSequences.length === 0) {
        addLogEntry("DEMO", "El búfer histórico está vacío. Graba movimientos primero.", "text-red-400");
        return;
    }
    addLogEntry("DEMO", "Iniciando secuencia de reproducción automática...", "text-purple-400 font-bold");
    
    demoSequences.forEach((step, index) => {
        setTimeout(() => {
            send(step.direccion);
            // Envía un comando de parada automático a los 800ms de haber iniciado cada paso
            setTimeout(() => send("STOP"), 800); 
        }, index * 1500); // Intervalo de separación entre comandos secuenciales
    });
}

// ============================================================================
// CONTROLADOR DE LOGS VISUALES EN PANTALLA (AUDITORÍA HUD)
// ============================================================================
function addLogEntry(origen, texto, claseColor) {
    const container = document.getElementById("log-container");
    if (!container) return;
    
    const hora = new Date().toLocaleTimeString();
    const nuevaFila = document.createElement("div");
    nuevaFila.className = `py-0.5 border-b border-cyan-950/40 font-mono text-[11px] tracking-tight ${claseColor}`;
    nuevaFila.innerHTML = `<span>[${hora}] [${origen}] » ${texto}</span>`;
    
    container.insertBefore(nuevaFila, container.firstChild);

    // Mantiene un límite máximo de 30 registros en memoria visual para evitar sobrecarga del navegador
    if (container.children.length > 30) {
        container.removeChild(container.lastChild);
    }
}

// ============================================================================
// SISTEMA KEEP-ALIVE (HEARTBEAT) - PREVIENE ERRORES DE DESCONEXIÓN (WINERROR 10053)
// ============================================================================
// Envía un pequeño pulso vacío de control cada 10 segundos para mantener el puerto activo
setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ ping: true }));
    }
}, 10000);

// Inicialización automática al cargar el árbol DOM
window.addEventListener("DOMContentLoaded", initWebSocket);