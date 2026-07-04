import React, { useState, useContext } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, Alert, ActivityIndicator } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Feather } from '@expo/vector-icons';
import BrandBackground from '../components/BrandBackground';
import LiquidButton from '../components/LiquidButton';
import { AuthContext } from '../contexts/AuthContext';
import { API_URL } from '../env';

const fetchWithTimeout = async (url, options = {}, ms = 20000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ms);

  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } catch (e) {
    console.warn('login fetchWithTimeout error:', e?.name, e?.message);
    if (e?.name === 'AbortError') {
      throw new Error(`Timeout: ${ms}ms. Revisa conectividad/IP o que el backend esté respondiendo.`);
    }
    if (e instanceof TypeError) {
      throw new Error(`No se pudo conectar al servidor (${API_URL}). Verifica IP/puerto y que FastAPI esté corriendo.`);
    }
    throw e;
  } finally {
    clearTimeout(timeoutId);
  }
};

/*zona2: main - hogar de los componentes */
export default function LoginScreen({ navigate, theme }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { setUserToken, setUserData } = useContext(AuthContext);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert("Error", "Por favor ingresa tu correo y contraseña");
      return;
    }
    
    setLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetchWithTimeout(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString()
      }, 20000);

      let data = null;
      try {
        data = await response.json();
      } catch {
        const txt = await response.text().catch(() => '');
        data = txt ? { detail: txt } : null;
      }

      if (!response.ok) {
        throw new Error(data?.detail || "Credenciales incorrectas");
      }

      const token = data.access_token;
      await AsyncStorage.setItem('userToken', token);

      const meResponse = await fetchWithTimeout(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      }, 20000);

      if (meResponse.ok) {
        const userInfo = await meResponse.json();
        setUserToken(token);
        setUserData(userInfo);
      } else {
        setUserToken(token);
      }

      navigate('Dashboard');
    } catch (error) {
      Alert.alert("Error de inicio de sesión", error?.message || "Error desconocido");
    } finally {
      setLoading(false);
    }
  };

  return (
    <BrandBackground theme={theme}>
      <KeyboardAvoidingView 
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.content}>
          <View style={styles.header}>
            <View style={[styles.logoBox, { backgroundColor: theme.colors.primary }]}>
              <Text style={styles.logoText}>S</Text>
            </View>
            <Text style={[styles.title, { color: theme.colors.textPrimary }]}>SAGE 2.0</Text>
            <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>Universidad Politécnica de Querétaro</Text>
          </View>

          <View style={[styles.glassCard, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
            <Text style={[styles.inputLabel, { color: theme.colors.textSecondary }]}>Correo Institucional</Text>
            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="book-open" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="valentina@upq.edu.mx"
                placeholderTextColor={theme.colors.textSecondary}
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <Text style={[styles.inputLabel, { color: theme.colors.textSecondary }]}>Contraseña</Text>
            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="lock" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="••••••••"
                placeholderTextColor={theme.colors.textSecondary}
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                <Feather name={showPassword ? "eye" : "eye-off"} size={18} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            </View>

            {loading ? (
              <ActivityIndicator size="large" color={theme.colors.primary} style={styles.buttonSpacing} />
            ) : (
              <LiquidButton 
                title="Ingresar" 
                theme={theme} 
                onPress={handleLogin} 
                style={styles.buttonSpacing} 
              />
            )}

            <TouchableOpacity onPress={() => navigate('ForgotPassword')} style={styles.linkContainer}>
              <Text style={[styles.forgotText, { color: theme.colors.primary }]}>¿Olvidaste tu contraseña?</Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={() => navigate('Register')} style={[styles.linkContainer, { marginTop: 8 }]}>
              <Text style={[styles.registerText, { color: theme.colors.textSecondary }]}>
                ¿No tienes cuenta? <Text style={{ color: theme.colors.primary, fontWeight: '700' }}>Regístrate</Text>
              </Text>
            </TouchableOpacity>
          </View>
          
          <Text style={[styles.footerText, { color: theme.colors.textSecondary }]}>Sistema exclusivo para estudiantes activos de UPQ</Text>
        </View>
      </KeyboardAvoidingView>
    </BrandBackground>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    padding: 24, // Grid 8px
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
  },
  logoBox: {
    width: 80,
    height: 80,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  logoText: {
    color: '#FFF',
    fontSize: 40,
    fontWeight: 'bold',
  },
  title: {
    fontSize: 24,
    fontWeight: '800',
    marginBottom: 4,
    letterSpacing: 0.5,
  },
  subtitle: {
    fontSize: 14,
    fontWeight: '400',
  },
  glassCard: {
    borderRadius: 24,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  inputLabel: {
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 8,
    marginLeft: 4,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 20,
    paddingHorizontal: 16,
    height: 52,
    backgroundColor: '#FAFAFA',
  },
  icon: {
    marginRight: 10,
  },
  eyeIcon: {
    padding: 8,
  },
  input: {
    flex: 1,
    height: '100%',
    fontSize: 15,
  },
  buttonSpacing: {
    marginTop: 8,
    marginBottom: 16,
  },
  linkContainer: {
    alignItems: 'center',
    marginBottom: 8,
  },
  forgotText: {
    fontSize: 14,
    fontWeight: '500',
  },
  registerText: {
    fontSize: 14,
    fontWeight: '500',
  },
  footerText: {
    marginTop: 32,
    fontSize: 11,
    textAlign: 'center',
  }
});
