import React, { useState, useEffect, useMemo, useContext } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import LiquidButton from '../components/LiquidButton';
import { AuthContext } from '../contexts/AuthContext';
import { API_URL } from '../env';

// Genera las próximas 7 fechas reales a partir de hoy
const generarFechasProximas = () => {
  const dias = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
  const meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
  const fechas = [];
  const hoy = new Date();

  for (let i = 0; i < 7; i++) {
    const d = new Date(hoy);
    d.setDate(hoy.getDate() + i);
    fechas.push({
      key: d.toISOString().split('T')[0],       // '2026-07-02'
      label: i === 0 ? 'Hoy' : dias[d.getDay()], // 'Hoy' o 'Lun'
      dia: d.getDate(),
      mes: meses[d.getMonth()],
    });
  }
  return fechas;
};

export default function AgendarScreen({ navigate, theme, params }) {
  const fechas = useMemo(() => generarFechasProximas(), []);
  const [selectedDateKey, setSelectedDateKey] = useState(fechas[0].key);
  const [selectedModulo, setSelectedModulo] = useState(null);
  const [selectedPC, setSelectedPC] = useState(null);
  const [loading, setLoading] = useState(false);
  const { userToken } = useContext(AuthContext);

  // Estados dinámicos
  const [modulos, setModulos] = useState([]);
  const [pcs, setPcs] = useState([]);
  const [ocupacionInfo, setOcupacionInfo] = useState({});

  // Datos del sitio desde navegación
  const sitio = params?.sitio || { id_espacio: 1, nombre: 'Laboratorio de Cómputo A', tipo: 'Laboratorio', capacidad: 30 };
  const esLaboratorio = sitio.tipo === 'Laboratorio';

  useEffect(() => {
    async function fetchData() {
      try {
        const resModulos = await fetch(`${API_URL}/reservas/modulos`, {
          headers: { 'Authorization': `Bearer ${userToken}` }
        });
        if (resModulos.ok) {
           const mods = await resModulos.json();
           setModulos(mods.map(m => ({
              id: m.id_modulo,
              label: m.nombre,
              inicio: m.hora_inicio,
              fin: m.hora_fin
           })));
        }

        if (esLaboratorio) {
          const resPcs = await fetch(`${API_URL}/equipos?espacio_id=${sitio.id_espacio}`, {
            headers: { 'Authorization': `Bearer ${userToken}` }
          });
          if (resPcs.ok) {
             const dataPcs = await resPcs.json();
             // Extraer el número del nombre_equipo o mostrarlo tal cual
             setPcs(dataPcs.map(pc => ({ 
               id: pc.id_equipo, 
               numero: pc.nombre_equipo.replace('PC-', '') 
             })));
          }
        }
      } catch(e) { console.warn(e); }
    }
    fetchData();
  }, [sitio.id_espacio, esLaboratorio, userToken]);

  useEffect(() => {
    async function fetchOcupacion() {
      try {
        const resOcupacion = await fetch(`${API_URL}/reservas/ocupacion?fecha=${selectedDateKey}`, {
          headers: { 'Authorization': `Bearer ${userToken}` }
        });
        if (resOcupacion.ok) {
           const data = await resOcupacion.json();
           setOcupacionInfo(data.ocupacion || {});
        }
      } catch(e) { console.warn(e); }
    }
    fetchOcupacion();
  }, [selectedDateKey, userToken]);

  const ocupados = useMemo(() => {
    if (!selectedModulo) return new Set();
    const mod = modulos.find(m => m.id === selectedModulo);
    if (!mod) return new Set();
    
    const set = new Set();
    Object.keys(ocupacionInfo).forEach(eqId => {
       const rangos = ocupacionInfo[eqId];
       // Check if there is overlap with mod.inicio, mod.fin
       // (Simplified: assuming string comparison of HH:MM is enough)
       const isOccupied = rangos.some(r => 
         (mod.inicio >= r.inicio && mod.inicio < r.fin) || 
         (mod.fin > r.inicio && mod.fin <= r.fin) ||
         (r.inicio >= mod.inicio && r.inicio < mod.fin)
       );
       if (isOccupied) set.add(parseInt(eqId));
    });
    return set;
  }, [selectedModulo, modulos, ocupacionInfo]);

  // Contadores
  const disponibles = pcs.length - ocupados.size;

  // Resetear PC al cambiar fecha o módulo
  const handleDateChange = (key) => {
    setSelectedDateKey(key);
    setSelectedPC(null);
  };
  const handleModuloChange = (id) => {
    setSelectedModulo(id);
    setSelectedPC(null);
  };

  const handleConfirm = async () => {
    if (!selectedModulo) {
      Alert.alert("Horario Requerido", "Selecciona un horario disponible antes de continuar.");
      return;
    }
    if (esLaboratorio && !selectedPC) {
      Alert.alert("Equipo Requerido", "Selecciona 1 computadora disponible en el mapa.");
      return;
    }

    const moduloInfo = modulos.find(m => m.id === selectedModulo);
    const fechaInfo = fechas.find(f => f.key === selectedDateKey);
    const fechaDisplay = fechaInfo.label === 'Hoy'
      ? `Hoy, ${fechaInfo.dia} ${fechaInfo.mes}`
      : `${fechaInfo.label} ${fechaInfo.dia} ${fechaInfo.mes}`;

    try {
      setLoading(true);
      const payload = {
        id_espacio: sitio.id_espacio || 1, // Fallback a 1
        id_equipo: esLaboratorio ? selectedPC : null,
        id_modulo: selectedModulo,
        fecha: selectedDateKey,
        observaciones: 'Reserva desde App Móvil'
      };

      const response = await fetch(`${API_URL}/reservas/estudiante`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || "No se pudo realizar la reserva");
      }

      Alert.alert(
        "✅ Reserva Confirmada",
        `${sitio.nombre}\n📅 ${fechaDisplay}\n⏰ ${moduloInfo.label}${esLaboratorio ? `\n💻 Equipo ${pcs.find(p=>p.id===selectedPC)?.numero}` : ''}`,
        [{
          text: "Ver mis reservas",
          onPress: () => navigate('MisReservas', { nuevaReserva: true })
        }]
      );
    } catch (error) {
      Alert.alert("Error de Reserva", error.message);
    } finally {
      setLoading(false);
    }
  };

  const isDark = theme.isDark;

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.secondary }]}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>

        {/* Header */}
        <View style={[styles.headerCard, { backgroundColor: theme.colors.cardBg }]}>
          <TouchableOpacity onPress={() => navigate('Sitios')} style={styles.backBtn}>
            <Feather name="arrow-left" size={24} color={theme.colors.textPrimary} />
            <Text style={[styles.backText, { color: theme.colors.textSecondary }]}>Espacios</Text>
          </TouchableOpacity>
          <View style={styles.headerInfo}>
            <View style={[styles.iconBox, { backgroundColor: '#EFF6FF' }]}>
              <Feather name={esLaboratorio ? "cpu" : "monitor"} size={28} color={theme.colors.primary} />
            </View>
            <View style={styles.headerTexts}>
              <Text style={[styles.title, { color: theme.colors.textPrimary }]}>{sitio.nombre}</Text>
              <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>Capacidad: {sitio.capacidad} personas</Text>
            </View>
          </View>
        </View>

        {/* ────── 1. FECHA ────── */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
            <Feather name="calendar" size={16} color={theme.colors.primary} /> Fecha
          </Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {fechas.map((f) => {
              const isActive = selectedDateKey === f.key;
              return (
                <TouchableOpacity
                  key={f.key}
                  style={[
                    styles.dateChip,
                    isActive
                      ? { backgroundColor: theme.colors.primary, borderColor: theme.colors.primary }
                      : { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }
                  ]}
                  onPress={() => handleDateChange(f.key)}
                >
                  <Text style={[styles.dateChipLabel, isActive ? { color: '#FFF' } : { color: theme.colors.textSecondary }]}>{f.label}</Text>
                  <Text style={[styles.dateChipDay, isActive ? { color: '#FFF' } : { color: theme.colors.textPrimary }]}>{f.dia}</Text>
                  <Text style={[styles.dateChipMonth, isActive ? { color: 'rgba(255,255,255,0.7)' } : { color: theme.colors.textSecondary }]}>{f.mes}</Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        </View>

        {/* ────── 2. HORARIO / MÓDULO ────── */}
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
            <Feather name="clock" size={16} color={theme.colors.primary} /> Horario
          </Text>
          <View style={styles.moduloGrid}>
            {modulos.map((m) => {
              const isActive = selectedModulo === m.id;
              return (
                <TouchableOpacity
                  key={m.id}
                  style={[
                    styles.moduloChip,
                    isActive
                      ? { backgroundColor: theme.colors.primary, borderColor: theme.colors.primary }
                      : { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }
                  ]}
                  onPress={() => handleModuloChange(m.id)}
                >
                  <Text style={[styles.moduloText, isActive ? { color: '#FFF' } : { color: theme.colors.textPrimary }]}>{m.label}</Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* ────── 3. MAPA DE EQUIPOS (solo Laboratorio) ────── */}
        {esLaboratorio && selectedModulo && (
          <View style={styles.section}>
            <View style={styles.sectionHeaderRow}>
              <Text style={[styles.sectionTitle, { color: theme.colors.textPrimary }]}>
                <Feather name="monitor" size={16} color={theme.colors.primary} /> Selecciona tu equipo
              </Text>
              <Text style={[styles.counterText, { color: theme.colors.success }]}>
                {disponibles} disponibles
              </Text>
            </View>

            <View style={[styles.cinemaContainer, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>

              {/* Pizarrón */}
              <View style={styles.screenIndicator}>
                <View style={[styles.screenBar, { backgroundColor: isDark ? '#374151' : '#E5E7EB' }]} />
                <Text style={[styles.screenText, { color: theme.colors.textSecondary }]}>Pizarrón</Text>
              </View>

              {/* Grid de PCs — 6 columnas con pasillo central */}
              <View style={styles.gridContainer}>
                {pcs.map((pc, index) => {
                  const isOcupado = ocupados.has(pc.id);
                  const isSelected = selectedPC === pc.id;

                  let bgColor = isDark ? '#374151' : '#F3F4F6';
                  let borderColor = isDark ? '#4B5563' : '#E5E7EB';
                  let textColor = theme.colors.textSecondary;
                  let iconName = 'monitor';

                  if (isOcupado) {
                    bgColor = isDark ? '#7F1D1D' : '#FEE2E2';
                    borderColor = '#FCA5A5';
                    textColor = theme.colors.error;
                    iconName = 'x';
                  } else if (isSelected) {
                    bgColor = theme.colors.primary;
                    borderColor = theme.colors.primary;
                    textColor = '#FFFFFF';
                    iconName = 'check';
                  }

                  // Pasillo central después de la columna 3
                  const colInRow = index % 6;
                  const marginRight = colInRow === 2 ? 20 : colInRow === 5 ? 0 : 6;

                  return (
                    <TouchableOpacity
                      key={pc.id}
                      disabled={isOcupado}
                      onPress={() => setSelectedPC(pc.id)}
                      activeOpacity={0.7}
                      style={[
                        styles.pcSeat,
                        { backgroundColor: bgColor, borderColor: borderColor, marginRight: marginRight }
                      ]}
                    >
                      {isSelected ? (
                        <Feather name="check" size={14} color={textColor} />
                      ) : (
                        <Text style={[styles.pcNumber, { color: textColor }]}>{pc.numero}</Text>
                      )}
                    </TouchableOpacity>
                  );
                })}
              </View>

              {/* Leyenda */}
              <View style={[styles.legendContainer, { borderTopColor: isDark ? '#374151' : '#F3F4F6' }]}>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: isDark ? '#374151' : '#F3F4F6', borderWidth: 1, borderColor: isDark ? '#4B5563' : '#E5E7EB' }]} />
                  <Text style={[styles.legendText, { color: theme.colors.textSecondary }]}>Disponible</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: isDark ? '#7F1D1D' : '#FEE2E2' }]} />
                  <Text style={[styles.legendText, { color: theme.colors.textSecondary }]}>Ocupado</Text>
                </View>
                <View style={styles.legendItem}>
                  <View style={[styles.legendDot, { backgroundColor: theme.colors.primary }]} />
                  <Text style={[styles.legendText, { color: theme.colors.textSecondary }]}>Tu lugar</Text>
                </View>
              </View>
            </View>
          </View>
        )}

        {/* Mensaje si no se ha seleccionado módulo */}
        {esLaboratorio && !selectedModulo && (
          <View style={[styles.hintCard, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
            <Feather name="info" size={20} color={theme.colors.primary} />
            <Text style={[styles.hintText, { color: theme.colors.textSecondary }]}>
              Selecciona un horario para ver los equipos disponibles
            </Text>
          </View>
        )}

        {/* Resumen de selección */}
        {selectedModulo && (
          <View style={[styles.summaryCard, { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder }]}>
            <Text style={[styles.summaryTitle, { color: theme.colors.textPrimary }]}>Resumen de tu reserva</Text>
            <View style={styles.summaryRow}>
              <Feather name="map-pin" size={14} color={theme.colors.primary} />
              <Text style={[styles.summaryText, { color: theme.colors.textSecondary }]}>{sitio.nombre}</Text>
            </View>
            <View style={styles.summaryRow}>
              <Feather name="calendar" size={14} color={theme.colors.primary} />
              <Text style={[styles.summaryText, { color: theme.colors.textSecondary }]}>
                {fechas.find(f => f.key === selectedDateKey)?.label === 'Hoy'
                  ? `Hoy, ${fechas.find(f => f.key === selectedDateKey)?.dia} ${fechas.find(f => f.key === selectedDateKey)?.mes}`
                  : `${fechas.find(f => f.key === selectedDateKey)?.label} ${fechas.find(f => f.key === selectedDateKey)?.dia} ${fechas.find(f => f.key === selectedDateKey)?.mes}`
                }
              </Text>
            </View>
            <View style={styles.summaryRow}>
              <Feather name="clock" size={14} color={theme.colors.primary} />
              <Text style={[styles.summaryText, { color: theme.colors.textSecondary }]}>
                {modulos.find(m => m.id === selectedModulo)?.label}
              </Text>
            </View>
            {esLaboratorio && selectedPC && (
              <View style={styles.summaryRow}>
                <Feather name="monitor" size={14} color={theme.colors.success} />
                <Text style={[styles.summaryText, { color: theme.colors.success, fontWeight: '700' }]}>Equipo {pcs.find(p=>p.id===selectedPC)?.numero}</Text>
              </View>
            )}
          </View>
        )}

        <View style={{ height: 120 }} />
      </ScrollView>

      {/* Botón flotante */}
      <View style={[styles.fabContainer, { backgroundColor: theme.colors.cardBg, borderTopColor: theme.colors.glassBorder }]}>
        {loading ? (
          <ActivityIndicator size="large" color={theme.colors.primary} />
        ) : (
          <LiquidButton
            title={
              !selectedModulo
                ? "Selecciona un horario"
                : esLaboratorio && !selectedPC
                  ? "Selecciona un equipo"
                  : esLaboratorio && selectedPC
                    ? `Confirmar Equipo ${pcs.find(p=>p.id===selectedPC)?.numero}`
                    : "Confirmar Reserva"
            }
            theme={theme}
            onPress={handleConfirm}
            style={styles.fab}
          />
        )}
      </View>
    </View>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { paddingHorizontal: 24, paddingTop: 60 },

  // Header
  headerCard: {
    padding: 24, borderRadius: 24, marginBottom: 28,
    shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.05, shadowRadius: 10, elevation: 2,
  },
  backBtn: { flexDirection: 'row', alignItems: 'center', marginBottom: 16 },
  backText: { marginLeft: 8, fontSize: 15, fontWeight: '500' },
  headerInfo: { alignItems: 'center' },
  iconBox: { width: 64, height: 64, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginBottom: 16 },
  headerTexts: { alignItems: 'center' },
  title: { fontSize: 22, fontWeight: '800', marginBottom: 4, textAlign: 'center' },
  subtitle: { fontSize: 14, fontWeight: '500' },

  // Secciones
  section: { marginBottom: 28 },
  sectionTitle: { fontSize: 16, fontWeight: '700', marginBottom: 14, marginLeft: 4 },
  sectionHeaderRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  counterText: { fontSize: 13, fontWeight: '700' },

  // Date chips (vertical style)
  dateChip: {
    width: 64, paddingVertical: 12, borderRadius: 16, borderWidth: 1, marginRight: 10, alignItems: 'center',
  },
  dateChipLabel: { fontSize: 11, fontWeight: '600', marginBottom: 4 },
  dateChipDay: { fontSize: 20, fontWeight: '800', marginBottom: 2 },
  dateChipMonth: { fontSize: 11, fontWeight: '500' },

  // Módulo chips
  moduloGrid: { flexDirection: 'row', flexWrap: 'wrap' },
  moduloChip: {
    paddingVertical: 12, paddingHorizontal: 16, borderRadius: 14, borderWidth: 1, marginRight: 10, marginBottom: 10,
  },
  moduloText: { fontWeight: '600', fontSize: 14 },

  // Cinema map
  cinemaContainer: {
    padding: 20, borderRadius: 24, borderWidth: 1, alignItems: 'center',
  },
  screenIndicator: { alignItems: 'center', marginBottom: 20, width: '100%' },
  screenBar: { height: 4, width: '40%', borderRadius: 2, marginBottom: 8 },
  screenText: { fontSize: 11, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 1 },
  gridContainer: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', width: '100%' },
  pcSeat: {
    width: 40, height: 40, borderRadius: 10, borderWidth: 1.5,
    alignItems: 'center', justifyContent: 'center', marginBottom: 10,
  },
  pcNumber: { fontSize: 12, fontWeight: '700' },
  legendContainer: {
    flexDirection: 'row', justifyContent: 'space-around', width: '100%',
    marginTop: 16, paddingTop: 16, borderTopWidth: 1,
  },
  legendItem: { flexDirection: 'row', alignItems: 'center' },
  legendDot: { width: 12, height: 12, borderRadius: 6, marginRight: 6 },
  legendText: { fontSize: 12, fontWeight: '500' },

  // Hint
  hintCard: {
    flexDirection: 'row', alignItems: 'center', padding: 16, borderRadius: 16, borderWidth: 1, marginBottom: 28,
  },
  hintText: { marginLeft: 12, fontSize: 14, fontWeight: '500', flex: 1 },

  // Summary
  summaryCard: {
    padding: 20, borderRadius: 20, borderWidth: 1, marginBottom: 16,
  },
  summaryTitle: { fontSize: 15, fontWeight: '700', marginBottom: 12 },
  summaryRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  summaryText: { marginLeft: 10, fontSize: 14, fontWeight: '500' },

  // FAB
  fabContainer: {
    position: 'absolute', bottom: 0, left: 0, right: 0, padding: 24, paddingBottom: 32,
    borderTopWidth: 1, borderTopLeftRadius: 32, borderTopRightRadius: 32,
    shadowColor: '#000', shadowOffset: { width: 0, height: -4 }, shadowOpacity: 0.05, shadowRadius: 10, elevation: 10,
  },
  fab: { borderRadius: 16, height: 56 },
});
