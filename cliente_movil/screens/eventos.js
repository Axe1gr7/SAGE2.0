import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import BottomNav from '../components/BottomNav';
import { API_URL } from '../env';

/*zona2: main - hogar de los componentes */
export default function EventosScreen({ navigate, theme }) {
  const [filtroActivo, setFiltroActivo] = useState('Todos');
  const [inscritos, setInscritos] = useState([]);
  const [eventos, setEventos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchEventos() {
      try {
        const response = await fetch(`${API_URL}/eventos/proximos`);
        if (response.ok) {
          const data = await response.json();
          const formatted = data.map(ev => {
            const isTaller = ev.nombre.toLowerCase().includes('taller');
            return {
              id: ev.id_evento.toString(),
              nombre: ev.nombre,
              tipo: isTaller ? 'Taller' : 'Seminario', // Basic heuristic
              fecha: ev.fecha_inicio.split('T')[0], // YYYY-MM-DD
              lugar: 'SAGE',
              disponible: true,
              bgTag: isTaller ? '#FEF3C7' : '#E0E7FF',
              colorTag: isTaller ? '#D97706' : '#4338CA'
            };
          });
          setEventos(formatted);
        }
      } catch(e) {
        console.warn(e);
      } finally {
        setLoading(false);
      }
    }
    fetchEventos();
  }, []);

  const eventosFiltrados = eventos.filter(e => {
    if (filtroActivo === 'Todos') return true;
    return e.tipo === filtroActivo || e.nombre.toLowerCase().includes(filtroActivo.toLowerCase());
  });

  const handleInscribir = (id) => {
    if (inscritos.includes(id)) return;
    Alert.alert("Éxito", "Te has inscrito al evento correctamente.");
    setInscritos([...inscritos, id]);
  };

  const renderItem = ({ item }) => {
    const estaInscrito = inscritos.includes(item.id);
    const estaAgotado = !item.disponible && !estaInscrito;

    return (
      <View style={[styles.card, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
        <View style={styles.cardHeader}>
          <View style={[styles.badge, { backgroundColor: item.bgTag }]}>
            <Text style={[styles.badgeText, { color: item.colorTag }]}>{item.tipo}</Text>
          </View>
          <Feather name="bookmark" size={20} color={theme.colors.textSecondary} />
        </View>
        
        <Text style={[styles.cardTitle, { color: theme.colors.textPrimary }]}>{item.nombre}</Text>
        
        <View style={styles.cardFooter}>
          <View style={styles.infoRow}>
            <Feather name="calendar" size={14} color={theme.colors.textSecondary} />
            <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>{item.fecha}</Text>
          </View>
          <View style={styles.infoRow}>
            <Feather name="map-pin" size={14} color={theme.colors.textSecondary} />
            <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>{item.lugar}</Text>
          </View>
        </View>
        
        <TouchableOpacity 
          style={[styles.actionBtn, { 
            backgroundColor: estaInscrito ? theme.colors.success : (estaAgotado ? '#F3F4F6' : theme.colors.primary) 
          }]}
          disabled={estaAgotado || estaInscrito}
          onPress={() => handleInscribir(item.id)}
        >
          <Text style={[styles.actionBtnText, { 
            color: estaInscrito ? '#FFF' : (estaAgotado ? '#9CA3AF' : '#FFF') 
          }]}>
            {estaInscrito ? 'Inscrito' : (estaAgotado ? 'Agotado' : 'Inscribirse')}
          </Text>
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.secondary }]}>
      <View style={styles.header}>
        <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Eventos y Talleres</Text>
        <Text style={[styles.headerSub, { color: theme.colors.textSecondary }]}>Descubre actividades extracurriculares</Text>
      </View>

      <View style={styles.filterContainer}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterScroll}>
          {['Todos', 'Talleres', 'Seminarios', 'Hackathons'].map((f) => {
            const isActive = filtroActivo === f;
            return (
              <TouchableOpacity 
                key={f}
                style={[
                  styles.filterChip,
                  isActive ? { backgroundColor: theme.colors.primary, borderColor: theme.colors.primary } : { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }
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
          data={eventosFiltrados}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
        />
      )}
      <BottomNav navigate={navigate} currentRoute="Eventos" theme={theme} />
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
    paddingBottom: 8,
  },
  headerTitle: {
    fontSize: 28,
    fontWeight: '800',
    marginBottom: 4,
  },
  headerSub: {
    fontSize: 14,
    fontWeight: '500',
  },
  filterContainer: {
    paddingLeft: 24,
    marginBottom: 16,
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
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  badge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  badgeText: {
    fontSize: 11,
    fontWeight: '700',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '700',
    marginBottom: 16,
    lineHeight: 24,
  },
  cardFooter: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  infoText: {
    marginLeft: 6,
    fontSize: 13,
    fontWeight: '500',
  },
  actionBtn: {
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
  },
  actionBtnText: {
    fontSize: 14,
    fontWeight: '700',
  }
});
