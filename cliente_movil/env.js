// Archivo de configuración de ambiente para el móvil.
// Recomendación: usa IP de tu PC en la misma red (LAN) para que el celular pueda acceder.

// Copia la info de env.example.js y ajusta la IP/puerto.

// Ejecutando el móvil localmente (sin docker) necesitas que la API sea accesible
// desde el dispositivo/emu:
// - Si usas Android Emulator/iOS Simulator a veces sirve localhost.
// - En físico usa la IP LAN de tu PC (misma red WiFi).
//
// Ajusta la URL según corresponda.
// En iOS/Android en dispositivo/emulador, `localhost` apunta al propio dispositivo.
// En Expo Go/Simulators normalmente funciona, pero si falla, usa IP LAN de tu Mac.
// Cambia la IP 192.168.x.x según tu red.
export const API_URL = 'http://192.168.0.129:8080';



