/*zona1: importaciones de componentes y archivos */
import React from 'react';
import { TouchableOpacity, Text, StyleSheet, View } from 'react-native';

/*zona2: main - hogar de los componentes */
export default function LiquidButton({ onPress, title, theme, style, icon }) {
  return (
    <TouchableOpacity onPress={onPress} style={[styles.button, { backgroundColor: theme.colors.primary }, style]} activeOpacity={0.8}>
      {/* Efecto Glass overlay simulado */}
      <View style={[styles.glassOverlay, { borderColor: theme.colors.glassBorder }]} />
      
      {icon && <View style={styles.iconContainer}>{icon}</View>}
      <Text style={styles.text}>{title}</Text>
    </TouchableOpacity>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  button: {
    height: 56,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'row',
    position: 'relative',
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  glassOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.15)', // Liquid glass reflection
    borderTopWidth: 1,
    borderLeftWidth: 1,
    borderRadius: 12,
  },
  iconContainer: {
    marginRight: 8,
  },
  text: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    zIndex: 2,
  },
});
