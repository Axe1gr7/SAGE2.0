import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, Alert } from 'react-native';
import { Feather } from '@expo/vector-icons';
import BrandBackground from '../components/BrandBackground';
import LiquidButton from '../components/LiquidButton';

/*zona2: main - hogar de los componentes */
export default function ForgotPasswordScreen({ navigate, theme }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleResetPassword = () => {
    if (!name || !email || !newPassword) {
      Alert.alert("Error", "Por favor completa todos los campos para validar tu identidad.");
      return;
    }
    
    // Validación de identidad simulada
    if (email.toLowerCase() === 'valentina@upq.edu.mx' && name.toLowerCase().includes('valentina')) {
      Alert.alert("Éxito", "Identidad validada. Tu contraseña ha sido actualizada correctamente.", [
        { text: "Ir a Login", onPress: () => navigate('Login') }
      ]);
    } else {
      Alert.alert("Error de Validación", "El nombre no coincide con el registro asociado a este correo.");
    }
  };

  return (
    <BrandBackground theme={theme}>
      <KeyboardAvoidingView 
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <View style={styles.content}>
          <TouchableOpacity onPress={() => navigate('Login')} style={styles.backBtn}>
            <Feather name="arrow-left" size={24} color={theme.colors.textSecondary} />
            <Text style={[styles.backText, { color: theme.colors.textSecondary }]}>Volver al Login</Text>
          </TouchableOpacity>

          <View style={styles.header}>
            <Text style={[styles.title, { color: theme.colors.primary }]}>Recuperar Contraseña</Text>
            <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>Valida tu identidad para continuar</Text>
          </View>

          <View style={[styles.glassCard, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
            
            <Text style={[styles.inputLabel, { color: theme.colors.textSecondary }]}>Nombre Completo Registrado</Text>
            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="user" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="Ej. Valentina Rivera"
                placeholderTextColor={theme.colors.textSecondary}
                value={name}
                onChangeText={setName}
                autoCapitalize="words"
              />
            </View>

            <Text style={[styles.inputLabel, { color: theme.colors.textSecondary }]}>Correo Institucional</Text>
            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="mail" size={18} color={theme.colors.textSecondary} style={styles.icon} />
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

            <Text style={[styles.inputLabel, { color: theme.colors.textSecondary }]}>Nueva Contraseña</Text>
            <View style={[styles.inputContainer, { borderColor: theme.colors.glassBorder }]}>
              <Feather name="lock" size={18} color={theme.colors.textSecondary} style={styles.icon} />
              <TextInput
                style={[styles.input, { color: theme.colors.textPrimary }]}
                placeholder="••••••••"
                placeholderTextColor={theme.colors.textSecondary}
                value={newPassword}
                onChangeText={setNewPassword}
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)} style={styles.eyeIcon}>
                <Feather name={showPassword ? "eye" : "eye-off"} size={18} color={theme.colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <LiquidButton 
              title="Cambiar Contraseña" 
              theme={theme} 
              onPress={handleResetPassword} 
              style={styles.buttonSpacing} 
            />
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
  backBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 32,
  },
  backText: {
    marginLeft: 8,
    fontSize: 16,
    fontWeight: '500',
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 15,
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
    marginTop: 16,
    marginBottom: 8,
  },
});
