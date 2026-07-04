import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, Alert, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import BrandBackground from '../components/BrandBackground';
import LiquidButton from '../components/LiquidButton';
import { API_URL } from '../env';

console.log('RegisterScreen API_URL:', API_URL);

const fetchWithTimeout = async (url, options = {}, ms = 20000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ms);

  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } catch (e) {
    console.warn('register fetchWithTimeout error:', e?.name, e?.message);
    if (e?.name === 'AbortError') {
      throw new Error(`Timeout: ${ms}ms. Revisa conectividad/IP o que el backend esté respondiendo.`);
    }
    // En RN/Expo, errores de red suelen ser TypeError: Network request failed
    if (e instanceof TypeError) {
      throw new Error(`No se pudo conectar al servidor (${API_URL}). Verifica IP/puerto y que FastAPI esté corriendo.`);
    }
    throw e;
  } finally {
    clearTimeout(timeoutId);
  }
};

/*zona2: main - hogar de los componentes */
export default function RegisterScreen({ navigate, theme }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [matricula, setMatricula] = useState('');
  // Debe coincidir con el enum CarreraEnum del backend (strings exactos)
  // En backend: 'sistemas', 'mecatronica', 'ingenieria de datos', ...
  const [carrera, setCarrera] = useState('sistemas');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    if (!name || !email || !password || !matricula) {
      Alert.alert("Campos requeridos", "Por favor completa todos los campos.");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        nombre_completo: name,
        matricula: matricula,
        correo: email,
        contrasena: password,
        carrera: carrera
      };

      const response = await fetchWithTimeout(
        `${API_URL}/auth/registro`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        },
        8000
      );

      let data = null;
      try {
        data = await response.json();
      } catch {
        const txt = await response.text().catch(() => '');
        data = txt ? { detail: txt } : null;
      }

      if (!response.ok) {
        throw new Error(data?.detail || 'Error al registrarse');
      }

      Alert.alert("Registro Exitoso", "Tu cuenta ha sido creada. Inicia sesión.", [
        { text: "Aceptar", onPress: () => navigate('Login') }
      ]);
    } catch (error) {
      Alert.alert("Error", error?.message || "Error desconocido");
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
            <Text style={[styles.title, { color: theme.colors.primary }]}>Crear Cuenta</Text>
            <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>Únete a SAGE 2.0</Text>
          </View>

          <View style={[styles.glassCard, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>

            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="user" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="Nombre Completo"
                placeholderTextColor={theme.colors.textSecondary}
                value={name}
                onChangeText={setName}
              />
            </View>

            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="hash" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="Matrícula"
                placeholderTextColor={theme.colors.textSecondary}
                value={matricula}
                onChangeText={setMatricula}
                keyboardType="number-pad"
              />
            </View>

            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="mail" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="Correo Institucional"
                placeholderTextColor={theme.colors.textSecondary}
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
              />
            </View>

            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="lock" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="Contraseña"
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
                  title="Registrarse"
                  theme={theme}
                  onPress={handleRegister}
                  style={styles.buttonSpacing}
                />
            )}

            <TouchableOpacity onPress={() => navigate('Login')} style={styles.linkContainer}>
              <Text style={[styles.linkText, { color: theme.colors.primary }]}>¿Ya tienes cuenta? Inicia sesión</Text>
            </TouchableOpacity>
          </View>
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
  title: {
    fontSize: 32,
    fontWeight: '800',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
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
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 16,
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
    marginTop: 8,
  },
  linkText: {
    fontSize: 14,
    fontWeight: '600',
  },
});
