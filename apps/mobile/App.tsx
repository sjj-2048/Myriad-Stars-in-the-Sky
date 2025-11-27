import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { magnitudeLabels, slogan, type StarLevel } from "@mystar/shared";

type HealthResponse = {
  data?: {
    health: string;
  };
};

export default function App() {
  const [health, setHealth] = useState<string>("loading");

  useEffect(() => {
    const query = `query { health }`;
    fetch("http://localhost:8000/graphql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })
      .then((res) => res.json() as Promise<HealthResponse>)
      .then((json) => setHealth(json.data?.health ?? "error"))
      .catch(() => setHealth("offline"));
  }, []);

  const level: StarLevel = "L2";

  return (
    <View style={styles.container}>
      <Text style={styles.caption}>MyriadStar</Text>
      <Text style={styles.title}>{slogan}</Text>
      <Text style={styles.text}>GraphQL health: {health}</Text>
      <Text style={styles.text}>
        示例星等：{magnitudeLabels[level]} ({level})
      </Text>
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
    color: "#94a3b8",
    letterSpacing: 6,
    textTransform: "uppercase",
  },
  title: {
    color: "#f8fafc",
    fontSize: 28,
    marginVertical: 12,
  },
  text: {
    color: "#cbd5f5",
    textAlign: "center",
  },
});
