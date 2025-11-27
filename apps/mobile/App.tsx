import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.caption}>MyriadStar</Text>
      <Text style={styles.title}>掌上星主控制台</Text>
      <Text style={styles.text}>即将支持星等面板、星尘上传、星试报名。</Text>
      <StatusBar style="light" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#020617',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
  caption: {
    color: '#94a3b8',
    letterSpacing: 6,
    textTransform: 'uppercase',
  },
  title: {
    color: '#f8fafc',
    fontSize: 28,
    marginVertical: 12,
  },
  text: {
    color: '#cbd5f5',
    textAlign: 'center',
  },
});
