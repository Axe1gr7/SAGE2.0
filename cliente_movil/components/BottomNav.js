/*zona1: importaciones de componentes y archivos */
import React from 'react';
import { View, TouchableOpacity, StyleSheet, Text } from 'react-native';
import { Feather } from '@expo/vector-icons';

/*zona2: main - hogar de los componentes */
export default function BottomNav({ navigate, currentRoute, theme }) {
  const tabs = [
    { route: 'Dashboard', icon: 'home', label: 'Inicio' },
    { route: 'Sitios', icon: 'search', label: 'Explorar' },
    { route: 'Eventos', icon: 'calendar', label: 'Eventos' },
    { route: 'MisReservas', icon: 'bookmark', label: 'Reservas' },
    { route: 'Perfil', icon: 'user', label: 'Perfil' },
  ];

  return (
    <View style={[styles.navContainer, { backgroundColor: theme.colors.cardBg, borderTopColor: theme.colors.glassBorder }]}>
      {tabs.map((tab) => {
        const isActive = currentRoute === tab.route;
        return (
          <TouchableOpacity 
            key={tab.route} 
            style={styles.tab} 
            onPress={() => navigate(tab.route)}
          >
            <Feather 
              name={tab.icon} 
              size={24} 
              color={isActive ? theme.colors.primary : theme.colors.textSecondary} 
            />
            <Text style={[
              styles.label, 
              { color: isActive ? theme.colors.primary : theme.colors.textSecondary },
              isActive && styles.labelActive
            ]}>
              {tab.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  navContainer: {
    flexDirection: 'row',
    height: 70,
    borderTopWidth: 1,
    paddingBottom: 15,
    paddingTop: 10,
    justifyContent: 'space-around',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: -4 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 10,
  },
  tab: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  label: {
    fontSize: 10,
    marginTop: 4,
    fontWeight: '500',
  },
  labelActive: {
    fontWeight: '700',
  }
});
