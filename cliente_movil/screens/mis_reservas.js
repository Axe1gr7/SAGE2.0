import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import BottomNav from '../components/BottomNav';
import { AuthContext } from '../contexts/AuthContext';
import { API_URL } from '../env';

/* helper local: fetch con timeout + abort */
const fetchWithTimeout = async (url, options = {}, ms = 20000) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), ms);

  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    return res;
  } catch (e) {
    console.warn('mis_reservas fetchWithTimeout error:', e?.name, e?.message);
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

// Datos de ejemplo persistidos en la sesión de la app
const reservasIniciales = [
  {
    id: '1',
    nombre: 'Laboratorio de Cómputo A',
    fecha: 'Hoy, 2 Jul',
    horario: '09:00 - 11:00',
    detalle: 'Equipo PC-12',
    estado: 'Confirmada',
    tipo: 'Proximas',
  },
  {
    id: '2',
    nombre: 'Auditorio Principal',
    fecha: 'Jue 3 Jul',
    horario: '14:00 - 16:00',
    detalle: 'Evento General',
    estado: 'Confirmada',
    tipo: 'Proximas',
  },
  {
    id: '3',
    nombre: 'Laboratorio de Cómputo A',
    fecha: '25 Jun 2025',
    horario: '09:00 - 11:00',
    detalle: 'Equipo PC-5',
    estado: 'Completada',
    tipo: 'Pasadas',
  },
];

export default function MisReservasScreen({ navigate, theme, params }) {
  const [tab, setTab] = useState('Proximas');
  const [reservas, setReservas] = useState([]);
  const [espacios, setEspacios] = useState({});
  const [loading, setLoading] = useState(true);
  const { userToken, setUserToken, setUserData } = useContext(AuthContext);

  const safeParse = async (res) => {
    try {
      return await res.json();
    } catch {
      try {
        const txt = await res.text();
        return txt ? { detail: txt } : null;
      } catch {
        return null;
      }
    }
  };

  const logoutAndRedirect = async () => {
    try {
      await AsyncStorage.removeItem('userToken');
      await AsyncStorage.removeItem('userData');
    } catch (_) {}
    setUserToken(null);
    setUserData(null);
    navigate('Login');
  };

  const fetchDatos = async () => {
    try {
      setLoading(true);

      // Si no hay token, sal
      if (!userToken) {
        setReservas([]);
        setEspacios({});
        return;
      }

      // Obtener espacios para mapear IDs a nombres
      const resEspacios = await fetchWithTimeout(
        `${API_URL}/espacios`,
        { headers: { Authorization: `Bearer ${userToken}` } }
      );

      if (resEspacios.status === 401 || resEspacios.status === 403) {
        await logoutAndRedirect();
        return;
      }

      const dataEspacios = await safeParse(resEspacios);
      const mapaEspacios = {};
      if (Array.isArray(dataEspacios)) {
        dataEspacios.forEach(e => (mapaEspacios[e.id_espacio] = e.nombre));
      }
      setEspacios(mapaEspacios);

      // Obtener reservas
      const resReservas = await fetchWithTimeout(
        `${API_URL}/reservas/`,
        { headers: { Authorization: `Bearer ${userToken}` } }
      );

      if (resReservas.status === 401 || resReservas.status === 403) {
        await logoutAndRedirect();
        return;
      }

      const dataReservas = await safeParse(resReservas);

      if (Array.isArray(dataReservas)) {
        const formateadas = dataReservas.map(r => {
          const isPasada = new Date(r.fecha_hora_fin) < new Date();
          const isCancelada = r.estado === 'cancelada';
          const isCompletada = isPasada && !isCancelada;

          let estadoFinal =
            r.estado === 'activa'
              ? 'Confirmada'
              : (r.estado === 'cancelada' ? 'Cancelada' : 'Completada');
          if (isCompletada) estadoFinal = 'Completada';

          const fInicio = new Date(r.fecha_hora_inicio);
          const fFin = new Date(r.fecha_hora_fin);

          return {
            id: r.id_reserva.toString(),
            nombre: mapaEspacios[r.id_espacio] || `Espacio ${r.id_espacio}`,
            fecha: fInicio.toLocaleDateString(),
            horario: `${fInicio.getHours().toString().padStart(2, '0')}:${fInicio.getMinutes().toString().padStart(2, '0')} - ${fFin.getHours().toString().padStart(2, '0')}:${fFin.getMinutes().toString().padStart(2, '0')}`,
            detalle: r.id_equipo ? `Equipo PC-${r.id_equipo}` : 'Espacio completo',
            estado: estadoFinal,
            tipo: isPasada || isCancelada ? 'Pasadas' : 'Proximas',
            raw: r
          };
        });
        setReservas(formateadas);
      }
    } catch (error) {
      console.warn('Error fetching reservas:', error);
      Alert.alert('Error', error?.message || 'No se pudo cargar tus reservas.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (userToken) {
      fetchDatos();
    } else {
      setLoading(false);
    }
  }, [userToken]);

  // Si llega una nueva reserva localmente, recargar la lista
  useEffect(() => {
    if (params?.nuevaReserva) {
      fetchDatos();
      setTab('Proximas');
    }
  }, [params?.nuevaReserva]);

  const handleCancel = (id) => {
    Alert.alert(
      "Cancelar Reserva",
      "¿Estás seguro que deseas cancelar esta reserva? Esta acción no se puede deshacer.",
      [
        { text: "No, mantener", style: "cancel" },
        {
          text: "Sí, cancelar",
          style: "destructive",
          onPress: async () => {
            try {
              const response = await fetch(`${API_URL}/reservas/${id}/cancelar?motivo=Cancelada por usuario`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${userToken}` }
              });
              if (!response.ok) throw new Error("Error al cancelar");
              
              setReservas(prev =>
                prev.map(r => r.id === id ? { ...r, estado: 'Cancelada', tipo: 'Pasadas' } : r)
              );
              Alert.alert("Reserva Cancelada", "Tu reserva ha sido cancelada exitosamente.");
            } catch (error) {
              Alert.alert("Error", error.message);
            }
          }
        }
      ]
    );
  };

  const handleShowCode = (item) => {
    // Genera un código de acceso simulado basado en el id
    const code = `SAGE-${item.id.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 4)}-${Math.floor(Math.random() * 9000 + 1000)}`;
    Alert.alert("🔑 Código de Acceso", `Tu código para ${item.nombre}:\n\n${code}\n\nMuéstralo al llegar al espacio.`);
  };

  const reservasFiltradas = reservas.filter(r => r.tipo === tab);

  const renderItem = ({ item }) => {
    const isConfirmada = item.estado === 'Confirmada';
    const isCancelada = item.estado === 'Cancelada';
    const isCompleted = item.estado === 'Completada';

    let badgeBg = '#D1FAE5';
    let badgeColor = '#059669';
    if (isCancelada) { badgeBg = '#FEE2E2'; badgeColor = '#DC2626'; }
    else if (isCompleted) { badgeBg = '#F3F4F6'; badgeColor = '#4B5563'; }

    const esPc = item.detalle.includes('PC');

    return (
      <View style={[styles.card, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
        {/* Header */}
        <View style={styles.cardHeader}>
          <View style={styles.cardTitleRow}>
            <View style={[styles.cardIcon, { backgroundColor: esPc ? '#EFF6FF' : '#FFF7ED' }]}>
              <Feather name={esPc ? "monitor" : "map-pin"} size={18} color={esPc ? theme.colors.primary : theme.colors.accent} />
            </View>
            <View style={styles.cardTitleTexts}>
              <Text style={[styles.cardTitle, { color: theme.colors.textPrimary }]} numberOfLines={1}>{item.nombre}</Text>
              <Text style={[styles.cardDetalle, { color: theme.colors.textSecondary }]}>{item.detalle}</Text>
            </View>
          </View>
          <View style={[styles.badge, { backgroundColor: badgeBg }]}>
            <Text style={[styles.badgeText, { color: badgeColor }]}>{item.estado}</Text>
          </View>
        </View>

        {/* Info */}
        <View style={styles.cardBody}>
          <View style={styles.infoRow}>
            <Feather name="calendar" size={14} color={theme.colors.textSecondary} />
            <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>{item.fecha}</Text>
          </View>
          <View style={styles.infoRow}>
            <Feather name="clock" size={14} color={theme.colors.textSecondary} />
            <Text style={[styles.infoText, { color: theme.colors.textSecondary }]}>{item.horario}</Text>
          </View>
        </View>

        {/* Acciones */}
        {isConfirmada && (
          <View style={styles.cardFooter}>
            <TouchableOpacity
              style={[styles.actionBtnOutline, { borderColor: theme.colors.primary }]}
              onPress={() => handleShowCode(item)}
            >
              <Feather name="key" size={14} color={theme.colors.primary} />
              <Text style={[styles.actionBtnOutlineText, { color: theme.colors.primary }]}>Código</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.actionBtnDanger, { backgroundColor: '#FEF2F2', borderColor: '#FECACA' }]}
              onPress={() => handleCancel(item.id)}
            >
              <Feather name="x-circle" size={14} color="#DC2626" />
              <Text style={[styles.actionBtnDangerText]}>Cancelar</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    );
  };

  const countProximas = reservas.filter(r => r.tipo === 'Proximas').length;
  const countPasadas = reservas.filter(r => r.tipo === 'Pasadas').length;

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.secondary }]}>
      <View style={styles.header}>
        <Text style={[styles.headerTitle, { color: theme.colors.textPrimary }]}>Mis Reservas</Text>
        <TouchableOpacity
          style={[styles.addBtn, { backgroundColor: theme.colors.primary }]}
          onPress={() => navigate('Sitios')}
        >
          <Feather name="plus" size={20} color="#FFF" />
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={styles.tabsContainer}>
        <View style={[styles.tabsBg, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
          <TouchableOpacity
            style={[styles.tab, tab === 'Proximas' && { backgroundColor: theme.colors.primary }]}
            onPress={() => setTab('Proximas')}
          >
            <Text style={[styles.tabText, tab === 'Proximas' ? { color: '#FFF' } : { color: theme.colors.textSecondary }]}>
              Próximas ({countProximas})
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, tab === 'Pasadas' && { backgroundColor: theme.colors.primary }]}
            onPress={() => setTab('Pasadas')}
          >
            <Text style={[styles.tabText, tab === 'Pasadas' ? { color: '#FFF' } : { color: theme.colors.textSecondary }]}>
              Pasadas ({countPasadas})
            </Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Lista */}
      {loading ? (
        <View style={styles.emptyContainer}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      ) : reservasFiltradas.length > 0 ? (
        <FlatList
          data={reservasFiltradas}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          refreshing={loading}
          onRefresh={fetchDatos}
        />
      ) : (
        <View style={styles.emptyContainer}>
          <View style={[styles.emptyIcon, { backgroundColor: theme.colors.cardBg }]}>
            <Feather name="inbox" size={40} color={theme.colors.glassBorder} />
          </View>
          <Text style={[styles.emptyTitle, { color: theme.colors.textPrimary }]}>
            Sin reservas {tab === 'Proximas' ? 'próximas' : 'pasadas'}
          </Text>
          <Text style={[styles.emptyText, { color: theme.colors.textSecondary }]}>
            {tab === 'Proximas' ? 'Explora los espacios y agenda tu lugar' : 'Aquí aparecerán tus reservas completadas'}
          </Text>
          {tab === 'Proximas' && (
            <TouchableOpacity
              style={[styles.emptyBtn, { backgroundColor: theme.colors.primary }]}
              onPress={() => navigate('Sitios')}
            >
              <Text style={styles.emptyBtnText}>Explorar Espacios</Text>
            </TouchableOpacity>
          )}
        </View>
      )}

      <BottomNav navigate={navigate} currentRoute="MisReservas" theme={theme} />
    </View>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  container: { flex: 1 },
  header: {
    padding: 24, paddingTop: 60, paddingBottom: 16,
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center',
  },
  headerTitle: { fontSize: 28, fontWeight: '800' },
  addBtn: {
    width: 40, height: 40, borderRadius: 14, justifyContent: 'center', alignItems: 'center',
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.1, shadowRadius: 4, elevation: 3,
  },

  // Tabs
  tabsContainer: { paddingHorizontal: 24, marginBottom: 20 },
  tabsBg: { flexDirection: 'row', borderRadius: 16, padding: 4, borderWidth: 1 },
  tab: { flex: 1, paddingVertical: 10, borderRadius: 12, alignItems: 'center' },
  tabText: { fontSize: 14, fontWeight: '600' },

  // List
  listContainer: { padding: 24, paddingTop: 0, paddingBottom: 100 },

  // Card
  card: {
    borderRadius: 20, padding: 18, marginBottom: 14, borderWidth: 1,
    shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.03, shadowRadius: 8, elevation: 1,
  },
  cardHeader: {
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 14,
  },
  cardTitleRow: { flexDirection: 'row', alignItems: 'center', flex: 1, marginRight: 8 },
  cardIcon: {
    width: 36, height: 36, borderRadius: 10, justifyContent: 'center', alignItems: 'center', marginRight: 12,
  },
  cardTitleTexts: { flex: 1 },
  cardTitle: { fontSize: 16, fontWeight: '700' },
  cardDetalle: { fontSize: 13, fontWeight: '500', marginTop: 2 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 8 },
  badgeText: { fontSize: 11, fontWeight: '700' },

  cardBody: { marginBottom: 14 },
  infoRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 6 },
  infoText: { marginLeft: 8, fontSize: 13, fontWeight: '500' },

  cardFooter: {
    flexDirection: 'row', justifyContent: 'space-between',
    paddingTop: 14, borderTopWidth: 1, borderTopColor: 'rgba(150,150,150,0.08)',
  },
  actionBtnOutline: {
    flexDirection: 'row', alignItems: 'center', paddingVertical: 8, paddingHorizontal: 14,
    borderRadius: 10, borderWidth: 1.5,
  },
  actionBtnOutlineText: { marginLeft: 6, fontSize: 13, fontWeight: '600' },
  actionBtnDanger: {
    flexDirection: 'row', alignItems: 'center', paddingVertical: 8, paddingHorizontal: 14,
    borderRadius: 10, borderWidth: 1,
  },
  actionBtnDangerText: { marginLeft: 6, fontSize: 13, fontWeight: '600', color: '#DC2626' },

  // Empty state
  emptyContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', paddingHorizontal: 40 },
  emptyIcon: {
    width: 80, height: 80, borderRadius: 24, justifyContent: 'center', alignItems: 'center', marginBottom: 16,
  },
  emptyTitle: { fontSize: 18, fontWeight: '700', marginBottom: 8 },
  emptyText: { fontSize: 14, fontWeight: '500', textAlign: 'center', lineHeight: 20, marginBottom: 24 },
  emptyBtn: {
    paddingVertical: 12, paddingHorizontal: 24, borderRadius: 12,
  },
  emptyBtnText: { color: '#FFF', fontSize: 14, fontWeight: '700' },
});
