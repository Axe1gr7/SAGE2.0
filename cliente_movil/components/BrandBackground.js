import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';

const { width, height } = Dimensions.get('window');

/*zona2: main - hogar de los componentes */
export default function BrandBackground({ theme, children }) {
  return (
    <View style={[styles.container, { backgroundColor: theme.colors.secondary }]}>
      {/* Fondo superior dividido para Login/Register */}
      <View style={[styles.topSplit, { backgroundColor: theme.colors.secondary }]} />
      
      {/* Contenido principal por encima */}
      <View style={styles.content}>
        {children}
      </View>
    </View>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  container: {
    flex: 1,
    position: 'relative',
  },
  content: {
    flex: 1,
    zIndex: 10,
  },
  topSplit: {
    position: 'absolute',
    width: '100%',
    height: '40%',
    top: 0,
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
});
