#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <BluetoothSerial.h>

// --- CONFIGURAÇÃO DE REDE (WIFI) ---
const char* ssid = "VALQUIRIA_2G";      // <--- EDITAR
const char* password = "sergio-gio"; // <--- EDITAR

// --- CONFIGURAÇÃO DE ALVO (BLUETOOTH DO ARDUINO) ---
// --- CONFIGURAÇÃO DE ALVO (BLUETOOTH DO ARDUINO) ---
String deviceName = "HC-05"; 
uint8_t address[6] = {0x58, 0x56, 0x00, 0x00, 0xD0, 0x55}; // MAC ENCONTRADO

// --- SERVIDOR ---
const char* serverUrl = "https://vinicolacaldart.onrender.com/api/readings";

BluetoothSerial SerialBT;
// --- IMPORTANTE: DEFINICAO DE VARIAVEIS GLOBAIS ---
// Removendo WiFiClient global, vamos usar local dentro da funcao para garantir limpeza de RAM
// address e serverUrl ja sao globais

void enviarParaNuvem(float t, float h) {
  if (WiFi.status() == WL_CONNECTED) {
    
    // 1. DESLIGA BLUETOOTH PARA LIBERAR RAM
    Serial.println("--- INICIANDO ENVIO HTTPS ---");
    Serial.print("RAM Antes: "); Serial.println(ESP.getFreeHeap());
    Serial.println("Desligando Bluetooth...");
    SerialBT.end(); 
    delay(1000); // Tempo para o sistema limpar a memoria
    Serial.print("RAM Pos-BT-Off: "); Serial.println(ESP.getFreeHeap());

    // 2. CONECTA VIA HTTPS (Agora temos memoria!)
    {
        WiFiClientSecure client;
        client.setInsecure(); // Ignora SSL
        const char* host = "vinicolacaldart.onrender.com";
        const int port = 443; // Voltamos para HTTPS

        Serial.print("Conectando seguro em "); Serial.println(host);
        
        if (client.connect(host, port)) {
            Serial.println("CONECTADO! Enviando...");
            
            String jsonPayload = "{\"temperatura\": " + String(t) + 
                                 ", \"umidade\": " + String(h) + 
                                 ", \"latitude\": -29.0305, \"longitude\": -51.1916, \"origem\": \"ESP32-Bridge\"}";

            client.println("POST /api/readings HTTP/1.1");
            client.print("Host: "); client.println(host);
            client.println("Content-Type: application/json");
            client.print("Content-Length: "); client.println(jsonPayload.length());
            client.println("Connection: close");
            client.println(); 
            client.println(jsonPayload);

            // Aguarda resposta
            unsigned long timeout = millis();
            while (client.available() == 0) {
                if (millis() - timeout > 10000) {
                    Serial.println("Timeout!");
                    break;
                }
            }

            // Le resposta
            Serial.println("Resposta do Servidor:");
            while(client.available()){
               char c = client.read();
               Serial.print(c);
            }
            Serial.println("\n-----------------------");
            
        } else {
             Serial.println("FALHA: HTTPS nao conectou mesmo sem BT.");
        }
        client.stop(); // Fecha conexao SSL
    }
    
    // 3. RELIGA BLUETOOTH
    Serial.println("Religando Bluetooth...");
    SerialBT.begin("ESP32_Bridge", true); 
    Serial.println("Reconectando ao Arduino...");
    if(SerialBT.connect(address)) {
        Serial.println("BT Reconectado!");
    } else {
        Serial.println("Falha ao reconectar BT (Tentara no Loop)");
    }

  } else {
    Serial.println("WiFi desconectado.");
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("--- INICIANDO ESP32 - FINAL ---");
  
  // 1. Conecta WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Conectado!");

  // Configura SSL Removed

  // 2. Inicia Bluetooth em modo MASTER (true)
  SerialBT.begin("ESP32_Bridge", true); 
  SerialBT.setPin("1234", 4);
  Serial.println("Bluetooth iniciado. Tentando conectar ao HC-05 (MAC)...");

  // Tenta conectar usando o ENDEREÇO MAC
  bool connected = SerialBT.connect(address);
  
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
     if (SerialBT.connect(address)) {
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

// (Funcao substituida acima)
