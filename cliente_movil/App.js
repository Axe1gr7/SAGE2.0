/*zona1: importaciones de componentes y archivos */
import { StatusBar } from 'expo-status-bar';
import React, { useState, createContext } from 'react';
import { StyleSheet, View, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Importar Pantallas (screens)
import LoginScreen from './screens/login';
import RegisterScreen from './screens/register';
import ForgotPasswordScreen from './screens/forgot_password';
import DashboardScreen from './screens/dashboard';
import SitiosScreen from './screens/sitios';
import AgendarScreen from './screens/agendar';
import EventosScreen from './screens/eventos';
import MisReservasScreen from './screens/mis_reservas';
import PerfilScreen from './screens/perfil'; // NUEVO - Pantalla de Perfil

import * as SplashScreen from 'expo-splash-screen';
import { AuthContext } from './contexts/AuthContext';

// Keep the splash screen visible while we fetch resources
SplashScreen.preventAutoHideAsync();

// Contexto para el Tema (Oscuro/Claro) y Autenticación
export const ThemeContext = createContext();

// URL base de la API FastAPI (debe ser accesible desde el dispositivo)
// IMPORTANTE: no uses localhost/127.0.0.1 en un celular físico.
import { API_URL } from './env';

console.log('App API_URL:', API_URL);

/*zona2: main - hogar de los componentes */
export default function App() {
  // Estado de navegación manual (simulando react-navigation)
  const [currentScreen, setCurrentScreen] = useState('Login');
  const [screenParams, setScreenParams] = useState({});
  // Estado del tema (light / dark)
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [appIsReady, setAppIsReady] = useState(false);
  
  // Estado de autenticación
  const [userToken, setUserToken] = useState(null);
  const [userData, setUserData] = useState(null);


  React.useEffect(() => {
    async function prepare() {
      // Timeout fuerte para que la pantalla NO se quede cargando
      const fetchWithTimeout = (url, options = {}, ms = 8000) => {
        let timeoutId;
        const timeoutPromise = new Promise((_, reject) => {
          timeoutId = setTimeout(() => reject(new Error(`Timeout: ${ms}ms`)), ms);
        });
        return Promise.race([
          fetch(url, options),
          timeoutPromise
        ]).finally(() => {
          if (timeoutId) clearTimeout(timeoutId);
        });
      };

      try {
        const token = await AsyncStorage.getItem('userToken');
        if (token) {
          const res = await fetchWithTimeout(
            `${API_URL}/auth/me`,
            {
              headers: { 'Authorization': `Bearer ${token}` }
            },
            8000
          );

          if (res && res.ok) {
            let user = null;
            try {
              user = await res.json();
            } catch (e) {
              // Si el backend regresó HTML/otra cosa, no rompemos el flujo.
              console.warn('Failed to parse /auth/me JSON');
            }

            setUserToken(token);
            setUserData(user);
            setCurrentScreen('Dashboard');
          } else {
            await AsyncStorage.removeItem('userToken');
          }
        }

        // Pequeña espera para dejar respirar al UI, sin congelar por red.
        await new Promise(resolve => setTimeout(resolve, 150));
      } catch (e) {
        console.warn('prepare() error:', e?.message || e);
      } finally {
        setAppIsReady(true);
      }
    }
    prepare();
  }, []);

  const onLayoutRootView = React.useCallback(async () => {
    if (appIsReady) {
      // This tells the splash screen to hide immediately
      await SplashScreen.hideAsync();
    }
  }, [appIsReady]);

  if (!appIsReady) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#FFFFFF' }}>
        <ActivityIndicator size="large" color="#2563EB" />
      </View>
    );
  }

  // Función para cambiar de pantalla
  const navigate = (screenName, params = {}) => {
    setScreenParams(params);
    setCurrentScreen(screenName);
  };

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
  };

  // Colores dinámicos del sistema de diseño SAGE 2.0
  const theme = {
    isDark: isDarkMode,
    colors: {
      primary: '#2563EB',      // Azul principal SAGE 2.0
      secondary: isDarkMode ? '#111827' : '#F4F6F8', // Fondo general más suave
      accent: '#F97316',       // Naranja para botones de acción (eventos)
      success: '#10B981',      // Verde (disponible, éxito)
      error: '#EF4444',        // Rojo (ocupado, cancelar)
      warning: '#F59E0B',      // Amarillo (pendiente)
      textPrimary: isDarkMode ? '#F9FAFB' : '#1F2937', 
      textSecondary: isDarkMode ? '#9CA3AF' : '#6B7280',
      cardBg: isDarkMode ? '#1F2937' : '#FFFFFF',
      glassBg: isDarkMode ? 'rgba(255, 255, 255, 0.05)' : 'rgba(255, 255, 255, 0.9)',
      glassBorder: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)',
    }
  };

  // Renderizador de pantallas
  const renderScreen = () => {
    switch (currentScreen) {
      case 'Login':
        return <LoginScreen navigate={navigate} theme={theme} params={screenParams} />;
      case 'Register':
        return <RegisterScreen navigate={navigate} theme={theme} params={screenParams} />;
      case 'ForgotPassword':
        return <ForgotPasswordScreen navigate={navigate} theme={theme} params={screenParams} />;
      case 'Dashboard':
        return <DashboardScreen navigate={navigate} theme={theme} toggleTheme={toggleTheme} params={screenParams} />;
      case 'Sitios':
        return <SitiosScreen navigate={navigate} theme={theme} params={screenParams} />;
      case 'Agendar':
        return <AgendarScreen navigate={navigate} theme={theme} params={screenParams} />;
      case 'Eventos':
        return <EventosScreen navigate={navigate} theme={theme} params={screenParams} />;
      case 'MisReservas':
        return <MisReservasScreen navigate={navigate} theme={theme} params={screenParams} />;
      case 'Perfil':
        return <PerfilScreen navigate={navigate} theme={theme} params={screenParams} toggleTheme={toggleTheme} />;
      default:
        return <LoginScreen navigate={navigate} theme={theme} params={screenParams} />;
    }
  };

  return (
    <AuthContext.Provider value={{ userToken, setUserToken, userData, setUserData }}>
      <ThemeContext.Provider value={theme}>
        <View style={[styles.container, { backgroundColor: theme.colors.secondary }]} onLayout={onLayoutRootView}>
          {renderScreen()}
          <StatusBar style={isDarkMode ? 'light' : 'dark'} />
        </View>
      </ThemeContext.Provider>
    </AuthContext.Provider>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
