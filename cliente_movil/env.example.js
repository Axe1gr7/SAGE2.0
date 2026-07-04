// Este archivo es un ejemplo. Copia y renómbralo como `env.js`.
// Ajusta los valores según tu máquina/dispositivo.

export const API_URL = {
  // Caso para emulador/iOS Simulator que a veces sí puede acceder a localhost
  // 'emulator': 'http://localhost:8080',

  // Caso típico para dispositivo físico: usar la IP LAN de tu computadora.
  // Ejemplo: http://192.168.1.50:8080
  'device': 'http://192.168.1.50:8080',

  // Caso para producción (si despliegas en servidor con dominio)
  // 'prod': 'https://tudominio.com'
};

