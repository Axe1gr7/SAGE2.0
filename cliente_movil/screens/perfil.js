import React, { useState } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  SafeAreaView, 
  SectionList, 
  Switch, 
  Pressable, 
  ImageBackground,
  Alert
} from 'react-native';
import { Feather } from '@expo/vector-icons';
import BottomNav from '../components/BottomNav';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthContext } from '../contexts/AuthContext';
import { API_URL } from '../env';

/*zona2: main - hogar de los componentes */
export default function PerfilScreen({ navigate, theme, toggleTheme }) {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const { userData, setUserToken, setUserData } = React.useContext(AuthContext);
  
  const firstName = userData?.nombre_completo ? userData.nombre_completo.split(' ')[0] : 'Usuario';
  const initial = firstName.charAt(0).toUpperCase();
  const email = userData?.correo || 'correo@upq.edu.mx';

  const confirmLogout = () => {
    Alert.alert(
      "Cerrar Sesión",
      "¿Estás seguro que deseas cerrar tu sesión actual?",
      [
        { text: "Cancelar", style: "cancel" },
        { text: "Cerrar Sesión", style: "destructive", onPress: async () => {
            await AsyncStorage.removeItem('userToken');
            await AsyncStorage.removeItem('userData');
            setUserToken(null);
            setUserData(null);
            navigate('Login');
        }}
      ]
    );
  };

  const sectionsData = [
    {
      title: 'Ajustes de la Aplicación',
      data: [
        { id: '1', title: 'Modo Oscuro', type: 'switch', value: theme.isDark, onValueChange: toggleTheme, icon: 'moon' },
        { id: '2', title: 'Notificaciones Push', type: 'switch', value: notificationsEnabled, onValueChange: () => setNotificationsEnabled(!notificationsEnabled), icon: 'bell' },
      ],
    },
    {
      title: 'Cuenta',
      data: [
        { id: '3', title: 'Editar Perfil', type: 'link', icon: 'user' },
        { id: '4', title: 'Privacidad y Seguridad', type: 'link', icon: 'shield' },
        { id: '5', title: 'Cerrar Sesión', type: 'action', icon: 'log-out', action: confirmLogout, color: theme.colors.error },
      ],
    },
  ];

  const renderItem = ({ item }) => {
    return (
      <Pressable 
        style={({ pressed }) => [
          styles.listItem, 
          { backgroundColor: theme.colors.cardBg, borderColor: theme.colors.glassBorder },
          pressed && { opacity: 0.7 }
        ]}
        onPress={item.type === 'action' ? item.action : null}
      >
        <View style={styles.itemLeft}>
          <Feather name={item.icon} size={20} color={item.color || theme.colors.primary} style={styles.itemIcon} />
          <Text style={[styles.itemText, { color: item.color || theme.colors.textPrimary }]}>{item.title}</Text>
        </View>
        
        {item.type === 'switch' && (
          <Switch
            trackColor={{ false: '#D1D5DB', true: theme.colors.primary }}
            thumbColor={'#FFFFFF'}
            ios_backgroundColor="#D1D5DB"
            onValueChange={item.onValueChange}
            value={item.value}
          />
        )}
        
        {item.type === 'link' && (
          <Feather name="chevron-right" size={20} color={theme.colors.textSecondary} />
        )}
      </Pressable>
    );
  };

  const renderSectionHeader = ({ section: { title } }) => (
    <Text style={[styles.sectionHeader, { color: theme.colors.textSecondary }]}>{title}</Text>
  );

  return (
    <SafeAreaView style={[styles.safeArea, { backgroundColor: theme.colors.secondary }]}>
      
      {/* Header con ImageBackground (Placeholder pattern o gradient) */}
      <ImageBackground 
        source={{ uri: 'https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=600&auto=format&fit=crop' }} 
        style={styles.headerBackground}
        imageStyle={{ borderBottomLeftRadius: 30, borderBottomRightRadius: 30 }}
      >
        <View style={styles.headerOverlay}>
          <View style={styles.profileAvatar}>
            <Text style={styles.avatarText}>{initial}</Text>
          </View>
          <Text style={styles.profileName}>{userData?.nombre_completo || 'Estudiante'}</Text>
          <Text style={styles.profileEmail}>{email}</Text>
        </View>
      </ImageBackground>

      <View style={styles.listContainer}>
        <SectionList
          sections={sectionsData}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          renderSectionHeader={renderSectionHeader}
          contentContainerStyle={styles.sectionListContent}
          showsVerticalScrollIndicator={false}
        />
      </View>
      
      <BottomNav navigate={navigate} currentRoute="Perfil" theme={theme} />
    </SafeAreaView>
  );
}

/*zona3: estilos y posicionamiento */
const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },
  headerBackground: {
    height: 220,
    width: '100%',
    justifyContent: 'flex-end',
  },
  headerOverlay: {
    backgroundColor: 'rgba(0,0,0,0.4)',
    height: '100%',
    width: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    borderBottomLeftRadius: 30,
    borderBottomRightRadius: 30,
  },
  profileAvatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 5,
    elevation: 5,
  },
  avatarText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2563EB',
  },
  profileName: {
    color: '#FFF',
    fontSize: 24,
    fontWeight: 'bold',
  },
  profileEmail: {
    color: '#E5E7EB',
    fontSize: 14,
    marginTop: 4,
  },
  listContainer: {
    flex: 1,
    paddingTop: 16,
  },
  sectionListContent: {
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  sectionHeader: {
    fontSize: 13,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: 24,
    marginBottom: 8,
    marginLeft: 4,
  },
  listItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 16,
    marginBottom: 8,
    borderWidth: 1,
  },
  itemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  itemIcon: {
    marginRight: 12,
  },
  itemText: {
    fontSize: 16,
    fontWeight: '500',
  }
});
