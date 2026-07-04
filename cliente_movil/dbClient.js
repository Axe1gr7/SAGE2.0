// Cliente simple (local) para guardar datos en AsyncStorage.
// Esto NO reemplaza la BD real; es solo persistencia en el dispositivo.
// Si necesitas persistencia real en BD del lado móvil (SQLite), dímelo.

import AsyncStorage from '@react-native-async-storage/async-storage';

const KEYS = {
  userToken: 'userToken',
  userData: 'userData',
};

export async function saveAuthToStorage({ token, userData }) {
  if (token) await AsyncStorage.setItem(KEYS.userToken, token);
  if (userData) await AsyncStorage.setItem(KEYS.userData, JSON.stringify(userData));
}

export async function loadAuthFromStorage() {
  const token = await AsyncStorage.getItem(KEYS.userToken);
  const userDataRaw = await AsyncStorage.getItem(KEYS.userData);
  const userData = userDataRaw ? JSON.parse(userDataRaw) : null;
  return { token, userData };
}

export async function clearAuthStorage() {
  await AsyncStorage.removeItem(KEYS.userToken);
  await AsyncStorage.removeItem(KEYS.userData);
}

