import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import BottomNav from '../components/BottomNav';
import { AuthContext } from '../contexts/AuthContext';
import { API_URL } from '../env';

/*zona2: main - hogar de los componentes */
export default function DashboardScreen({ navigate, theme, toggleTheme }) {
  const { userData } = React.useContext(AuthContext);
  const firstName = userData?.nombre_completo ? userData.nombre_completo.split(' ')[0] : 'Estudiante';
  const [eventos, setEventos] = useState([]);
  const [loadingEventos, setLoadingEventos] = useState(true);

  useEffect(() => {
    async function fetchEventos() {
      try {
        const response = await fetch(`${API_URL}/eventos/proximos`);
        if (response.ok) {
          const data = await response.json();
          setEventos(data.slice(0, 2)); // Mostrar solo los primeros 2
        }
      } catch (e) {
        console.warn(e);
      } finally {
        setLoadingEventos(false);
      }
    }
    fetchEventos();
  }, []);
  
  // En SAGE 2.0 el diseño base es muy limpio, predominantemente blanco
  return (
    <View style={[styles.container, { backgroundColor: theme.colors.secondary }]}>
      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        
        {/* Header SAGE 2.0 */}
        <View style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greetingGreeting}>Buenos días 👋</Text>
              <Text style={styles.greetingName}>Hola, {firstName}</Text>
            </View>
            <TouchableOpacity style={styles.bellBtn} onPress={toggleTheme}>
              {/* Uso toggleTheme en la campana de forma temporal para seguir teniendo la funcionalidad en demo */}
              <Feather name="bell" size={24} color={theme.colors.textPrimary} />
              <View style={styles.notificationBadge}>
                <Text style={styles.badgeText}>3</Text>
              </View>
            </TouchableOpacity>
          </View>
          
          <View style={[styles.searchContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
            <Feather name="search" size={18} color={theme.colors.textSecondary} />
            <TextInput 
              style={[styles.searchInput, { color: theme.colors.textPrimary }]} 
              placeholder="¿Qué espacio necesitas hoy?"
              placeholderTextColor={theme.colors.textSecondary}
            />
          </View>
        </View>

        {/* Carrusel de Talleres Recomendados */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Talleres Recomendados</Text>
            <TouchableOpacity onPress={() => navigate('Eventos')}>
              <Text style={[styles.seeAllText, { color: theme.colors.primary }]}>Ver todos</Text>
            </TouchableOpacity>
          </View>
          
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.carousel}>
            {loadingEventos ? (
               <ActivityIndicator size="small" color={theme.colors.primary} style={{marginLeft: 20}} />
            ) : eventos.length > 0 ? (
               eventos.map((ev, index) => {
                 const isTaller = ev.nombre.toLowerCase().includes('taller');
                 const bgCard = index % 2 === 0 ? '#F0F9FF' : '#F9FAFB';
                 const colorIcon = index % 2 === 0 ? theme.colors.primary : theme.colors.error;
                 const bgTag = isTaller ? '#FEF3C7' : '#E0E7FF';
                 const colorTag = isTaller ? '#D97706' : '#4338CA';
                 const tagText = isTaller ? 'Taller' : 'Seminario';
                 const fecha = ev.fecha_inicio.split('T')[0];

                 return (
                   <View key={ev.id_evento} style={[styles.cardTaller, { backgroundColor: bgCard }]}>
                     <View style={styles.cardIconBox}>
                       <Feather name={isTaller ? "zap" : "cpu"} size={24} color={colorIcon} />
                     </View>
                     <View style={[styles.tagBadge, { backgroundColor: bgTag }]}>
                       <Text style={[styles.tagText, { color: colorTag }]}>{tagText}</Text>
                     </View>
                     <Text style={[styles.cardTitle, { color: theme.colors.textPrimary }]} numberOfLines={2}>
                       {ev.nombre}
                     </Text>
                     <Text style={[styles.cardSub, { color: theme.colors.textSecondary }]}>{fecha}</Text>
                   </View>
                 );
               })
            ) : (
               <Text style={{marginLeft: 20, color: theme.colors.textSecondary}}>No hay eventos próximos.</Text>
            )}
          </ScrollView>
        </View>

        {/* Grid Acceso Rápido */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>Acceso Rápido</Text>
          <View style={styles.gridContainer}>
            <TouchableOpacity style={styles.gridItem} onPress={() => navigate('Sitios')}>
              <View style={[styles.iconContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
                <Feather name="monitor" size={24} color={theme.colors.primary} />
              </View>
              <Text style={[styles.gridText, { color: theme.colors.textSecondary }]}>Aulas</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.gridItem} onPress={() => navigate('Sitios')}>
              <View style={[styles.iconContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
                <Feather name="thermometer" size={24} color={theme.colors.success} />
              </View>
              <Text style={[styles.gridText, { color: theme.colors.textSecondary }]}>Laboratorios</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.gridItem} onPress={() => navigate('Sitios')}>
              <View style={[styles.iconContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
                <Feather name="mic" size={24} color={theme.colors.warning} />
              </View>
              <Text style={[styles.gridText, { color: theme.colors.textSecondary }]}>Auditorios</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.gridItem} onPress={() => navigate('Eventos')}>
              <View style={[styles.iconContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
                <Feather name="zap" size={24} color={theme.colors.error} />
              </View>
              <Text style={[styles.gridText, { color: theme.colors.textSecondary }]}>Talleres</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.gridItem} onPress={() => navigate('Sitios')}>
              <View style={[styles.iconContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
                <Feather name="coffee" size={24} color="#EC4899" />
              </View>
              <Text style={[styles.gridText, { color: theme.colors.textSecondary }]}>Salas</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.gridItem} onPress={() => navigate('Sitios')}>
              <View style={[styles.iconContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
                <Feather name="star" size={24} color="#6B7280" />
              </View>
              <Text style={[styles.gridText, { color: theme.colors.textSecondary }]}>Ver Todo</Text>
            </TouchableOpacity>
          </View>
        </View>
        
        {/* Espaciado inferior */}
        <View style={{ height: 40 }} />
      </ScrollView>
      <BottomNav navigate={navigate} currentRoute="Dashboard" theme={theme} />
    </View>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scroll: {
    flex: 1,
  },
  header: {
    padding: 24,
    paddingTop: 60,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greetingGreeting: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4,
  },
  greetingName: {
    fontSize: 24,
    fontWeight: '800',
    color: '#111827',
  },
  bellBtn: {
    position: 'relative',
    padding: 8,
  },
  notificationBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#F97316',
    borderRadius: 10,
    width: 18,
    height: 18,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#FFF',
  },
  badgeText: {
    color: '#FFF',
    fontSize: 10,
    fontWeight: 'bold',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 16,
    paddingHorizontal: 16,
    height: 54,
    borderWidth: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.02,
    shadowRadius: 4,
    elevation: 1,
  },
  searchInput: {
    flex: 1,
    marginLeft: 12,
    fontSize: 15,
  },
  section: {
    paddingHorizontal: 24,
    marginBottom: 32,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '800',
  },
  seeAllText: {
    fontSize: 14,
    fontWeight: '600',
  },
  carousel: {
    flexDirection: 'row',
  },
  cardTaller: {
    borderRadius: 20,
    width: 200,
    marginRight: 16,
    padding: 20,
  },
  cardIconBox: {
    marginBottom: 16,
  },
  tagBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    marginBottom: 12,
  },
  tagText: {
    fontSize: 10,
    fontWeight: '700',
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '700',
    marginBottom: 8,
    lineHeight: 20,
  },
  cardSub: {
    fontSize: 12,
    fontWeight: '500',
  },
  gridContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  gridItem: {
    alignItems: 'center',
    width: '30%',
    marginBottom: 20,
  },
  iconContainer: {
    width: 60,
    height: 60,
    borderRadius: 20,
    borderWidth: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 8,
    elevation: 2,
  },
  gridText: {
    fontSize: 12,
    fontWeight: '600',
  },
});
