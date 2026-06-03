function actualizarRelojHUD() {
    const ahora = new Date();
    
    const dia = String(ahora.getDate()).padStart(2, '0');
    const mes = String(ahora.getMonth() + 1).padStart(2, '0');
    const anio = ahora.getFullYear();
    
    // Captura segura de los contenedores del HUD
    const dateElement = document.getElementById("hud-date");
    const timeElement = document.getElementById("hud-time");
    
    // Blindaje condicional: Solo inyecta texto si los elementos existen en el HTML
    if (dateElement) {
        dateElement.innerText = `DATE: ${dia}-${mes}-${anio}`;
    }
    
    if (timeElement) {
        timeElement.innerText = `TIME: ${ahora.toLocaleTimeString()} STRK`;
    }
}

// Asegurar la inicialización una vez que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", () => {
    
    // Iniciar el ciclo asíncrono del reloj del sistema S.T.A.R.K.
    setInterval(actualizarRelojHUD, 1000);
    actualizarRelojHUD();

    // Captura segura del slider de velocidad
    const speedRange = document.getElementById("speed-range");
    const speedDisplay = document.getElementById("speed-display");

    // Escuchar cambios reactivos en el slider de forma segura
    if (speedRange && speedDisplay) {
        speedRange.addEventListener("input", (e) => {
            // Muestra el valor dinámico en pantalla (Ejemplo: 255 PWM o RPM según tu diseño)
            speedDisplay.innerText = `${e.target.value} PWM`;
        });
    }
});