#include <WiFi.h>
#include <HTTPClient.h>
#include <BluetoothSerial.h>

// --- CONFIGURAÇÃO DE REDE (WIFI) ---
const char* ssid = "VALQUIRIA_5G";      // <--- EDITAR
const char* password = "sergio-gio"; // <--- EDITAR

// --- CONFIGURAÇÃO DE ALVO (BLUETOOTH DO ARDUINO) ---
String deviceName = "HC-05"; // Nome do módulo Bluetooth do Arduino
// uint8_t address[6] = {0x00, 0x10, 0x00, 0x00, 0x00, 0x00}; // Se precisar conectar por MAC

// --- SERVIDOR ---
const char* serverUrl = "http://192.168.0.9:8000/api/readings";

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  
  // 1. Conecta WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Conectado!");

  // 2. Inicia Bluetooth em modo MASTER (true)
  SerialBT.begin("ESP32_Bridge", true); 
  Serial.println("Bluetooth iniciado. Tentando conectar ao HC-05...");

  // Tenta conectar (pode demorar um pouco)
  // O connect(name) retorna true se sucesso
  bool connected = SerialBT.connect(deviceName);
  
  if(connected) {
    Serial.println("Conectado ao HC-05 com sucesso!");
  } else {
    Serial.println("Falha ao conectar no HC-05. Reiniciando em 5s...");
    delay(5000);
    ESP.restart();
  }
}

String bufferLeitura = "";

void loop() {
  // Se perdeu conexão Bluetooth, tenta reconectar (simples)
  if (!SerialBT.connected(1000)) {
     Serial.println("Bluetooth desconectado! Tentando reconectar...");
     if (SerialBT.connect(deviceName)) {
        Serial.println("Reconectado!");
     }
  }

  // Ler dados do Bluetooth
  while (SerialBT.available()) {
    char c = SerialBT.read();
    
    // Se recebeu nova linha, processa a mensagem inteira
    if (c == '\n') {
      processaLinha(bufferLeitura);
      bufferLeitura = ""; // Limpa buffer
    } else {
      if (c != '\r') { // Ignora carriage return
        bufferLeitura += c;
      }
    }
  }
  
  delay(20);
}

void processaLinha(String linha) {
  Serial.println("Recebido do Arduino: " + linha);
  
  // Parse simples: "Temp: 25.00 | Umid: 65.00"
  // Vamos extrair os números.
  
  float temp = 0;
  float umid = 0;
  
  // Procura temperatura
  int idxT = linha.indexOf("Temp:");
  if (idxT != -1) {
    int fimT = linha.indexOf("|", idxT);
    String tStr = linha.substring(idxT + 5, fimT);
    temp = tStr.toFloat();
  }
  
  // Procura umidade
  int idxU = linha.indexOf("Umid:");
  if (idxU != -1) {
    String uStr = linha.substring(idxU + 5);
    umid = uStr.toFloat();
  }

  // Se leu algo valido, envia para WiFi
  if (temp > 0 || umid > 0) {
    enviarParaNuvem(temp, umid);
  }
}

void enviarParaNuvem(float t, float h) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.begin(client, serverUrl);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"temperatura\": " + String(t) + 
                         ", \"umidade\": " + String(h) + 
                         ", \"latitude\": -29.0305, \"longitude\": -51.1916, \"origem\": \"ESP32-Bridge\"}";
                         
    int responseCode = http.POST(jsonPayload);
    
    if (responseCode > 0) {
      Serial.println("Enviado para Nuvem! Code: " + String(responseCode));
    } else {
      Serial.println("Erro HTTP: " + String(responseCode));
    }
    http.end();
  } else {
    Serial.println("WiFi desconectado. Tentando reconectar...");
    WiFi.disconnect();
    WiFi.reconnect();
  }
}
