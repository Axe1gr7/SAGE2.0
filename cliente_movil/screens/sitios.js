import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import BottomNav from '../components/BottomNav';
import { API_URL } from '../env';

/*zona2: main - hogar de los componentes */
export default function SitiosScreen({ navigate, theme }) {
  const [filtroActivo, setFiltroActivo] = useState('Todos');
  const [espacios, setEspacios] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchEspacios() {
      try {
        // Importante: traer los espacios reales del backend
        const response = await fetch(`${API_URL}/espacios/`, {
          headers: {
            // Si el endpoint requiere auth, aquí lo puedes agregar.
            // En este screen no tenemos token, así que por ahora es anónimo.
          }
        });

        if (response.ok) {
          const data = await response.json();

          const formatted = data.map(esp => ({
            id: esp.id_espacio.toString(),
            nombre: esp.nombre,
            ubicacion: esp.edificio || 'Ubicación sin especificar',
            tipo: esp.tipo_espacio,
            capacidad: esp.capacidad,
            // Para mostrar “disponible” real necesitamos consultar ocupación/modulos.
            // Aquí lo dejamos como “true” visual hasta que el backend tenga un endpoint de disponibilidad por fecha.
            disponible: true
          }));

          setEspacios(formatted);
        } else {
          console.warn('fetchEspacios failed', response.status);
        }
      } catch (error) {
        console.warn(error);
      } finally {
        setLoading(false);
      }
    }
    fetchEspacios();
  }, []);


  const espaciosFiltrados = espacios.filter(e => {
    if (filtroActivo === 'Todos') return true;
    if (filtroActivo === 'Disponible') return e.disponible;
    return e.tipo === filtroActivo;
  });

  const getIconForType = (tipo) => {
    switch(tipo) {
      case 'Laboratorio': return { name: 'cpu', color: theme.colors.primary, bg: '#EFF6FF' };
      case 'Aula': return { name: 'monitor', color: theme.colors.accent, bg: '#FFF7ED' };
      case 'Auditorio': return { name: 'mic', color: theme.colors.success, bg: '#ECFDF5' };
      default: return { name: 'map-pin', color: theme.colors.textSecondary, bg: '#F3F4F6' };
    }
  };

  const renderItem = ({ item }) => {
    const iconData = getIconForType(item.tipo);
    return (
      <TouchableOpacity 
        style={[styles.card, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]} 
        onPress={() => navigate('Agendar', { sitio: item })}
        activeOpacity={0.8}
      >
        <View style={styles.cardHeader}>
          <View style={styles.titleRow}>
            <Text style={[styles.cardTitle, { color: theme.colors.textPrimary }]}>{item.nombre}</Text>
            <View style={[styles.badge, { backgroundColor: item.disponible ? '#D1FAE5' : '#FEE2E2' }]}>
              <Text style={[styles.badgeText, { color: item.disponible ? '#059669' : '#DC2626' }]}>
                {item.disponible ? 'Disponible' : 'Ocupado'}
              </Text>
            </View>
          </View>
          <Text style={[styles.cardSubtitle, { color: theme.colors.textSecondary }]}>{item.ubicacion}</Text>
        </View>
        
        <View style={styles.cardBody}>
          <View style={styles.infoRow}>
            <Feather name="users" size={14} color={theme.colors.textSecondary} />
            <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>{item.capacidad} personas</Text>
          </View>
          <View style={[styles.infoRow, { marginLeft: 16 }]}>
            <Feather name="map-pin" size={14} color={theme.colors.textSecondary} />
            <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>{item.tipo}</Text>
          </View>
        </View>

        {/* Icono de fondo decorativo o contenedor (simulado a la derecha) */}
        <View style={[styles.iconBox, { backgroundColor: iconData.bg }]}>
          <Feather name={iconData.name} size={32} color={iconData.color} />
        </View>
      </TouchableOpacity>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.secondary }]}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Explorar Espacios</Text>
          <TouchableOpacity style={[styles.filterBtn, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
            <Feather name="filter" size={20} color={theme.colors.primary} />
          </TouchableOpacity>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
          {['Todos', 'Disponible', 'Laboratorio', 'Aula', 'Deportivo'].map((f) => {
            const isActive = filtroActivo === f;
            return (
              <TouchableOpacity 
                key={f}
                style={[
                  styles.filterChip,
                  isActive ? { backgroundColor: theme.colors.primary } : { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }
                ]}
                onPress={() => setFiltroActivo(f)}
              >
                <Text style={[
                  styles.filterChipText,
                  isActive ? { color: '#FFF' } : { color: theme.colors.textSecondary }
                ]}>{f}</Text>
              </TouchableOpacity>
            )
          })}
        </ScrollView>
      </View>
      
      {loading ? (
        <ActivityIndicator size="large" color={theme.colors.primary} style={{flex:1, justifyContent:'center'}} />
      ) : (
        <FlatList
          data={espaciosFiltrados}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
        />
      )}
      <BottomNav navigate={navigate} currentRoute="Sitios" theme={theme} />
    </View>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    padding: 24,
    paddingTop: 60,
    paddingBottom: 16,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '800',
  },
  filterBtn: {
    padding: 10,
    borderRadius: 12,
    borderWidth: 1,
  },
  filterScroll: {
    flexDirection: 'row',
  },
  filterChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
  },
  filterChipText: {
    fontSize: 14,
    fontWeight: '600',
  },
  listContainer: {
    padding: 24,
    paddingTop: 8,
  },
  card: {
    borderRadius: 24,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.03,
    shadowRadius: 10,
    elevation: 2,
    position: 'relative',
    overflow: 'hidden',
  },
  cardHeader: {
    marginBottom: 20,
    zIndex: 2,
  },
  titleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 4,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    flex: 1,
    paddingRight: 8,
  },
  cardSubtitle: {
    fontSize: 13,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '700',
  },
  cardBody: {
    flexDirection: 'row',
    zIndex: 2,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  infoText: {
    marginLeft: 6,
    fontSize: 13,
    fontWeight: '500',
  },
  iconBox: {
    position: 'absolute',
    right: 20,
    bottom: 20,
    width: 60,
    height: 60,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    opacity: 0.8,
    zIndex: 1,
  }
});
