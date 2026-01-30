#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

// --- CONFIGURAÇÃO DE REDE ---
const char* ssid = "NOME_DO_WIFI";       // <--- EDITAR AQUI
const char* password = "SENHA_DO_WIFI";  // <--- EDITAR AQUI

// Endereço do Servidor (Seu IP Local encontrado: 192.168.0.9)
const char* serverUrl = "http://192.168.0.9:8000/api/readings";

// --- CONFIGURAÇÃO DO HARDWARE ---
// Conectar pino de DADOS do DHT22 no GPIO 4 (D4)
#define DHTPIN 4     
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Inicializa DHT
  dht.begin();

  // Conecta no Wi-Fi
  WiFi.begin(ssid, password);
  Serial.println("Conectando ao Wi-Fi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.print("Conectado! IP: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Aguarda 10 segundos entre envios
  delay(10000);

  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("Falha ao ler o sensor DHT!");
    return;
  }

  // Verifica conexão WiFi e reconecta se cair
  if(WiFi.status() != WL_CONNECTED){
    WiFi.disconnect();
    WiFi.reconnect();
    return;
  }

  // Envia POST Request
  WiFiClient client;
  HTTPClient http;

  // Inicia conexão
  http.begin(client, serverUrl);
  http.addHeader("Content-Type", "application/json");

  // Cria o JSON manual (String)
  // {"temperatura": 25.5, "umidade": 60.2, "origem": "ESP32-Winery"}
  String jsonPayload = "{\"temperatura\": " + String(t) + 
                       ", \"umidade\": " + String(h) + 
                       ", \"latitude\": -29.0305, \"longitude\": -51.1916, \"origem\": \"ESP32-Winery\"}";

  Serial.println("Enviando dados: " + jsonPayload);
  
  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Codigo HTTP: " + String(httpResponseCode));
    Serial.println("Resposta: " + response);
  } else {
    Serial.print("Erro ao enviar POST: ");
    Serial.println(httpResponseCode);
  }

  http.end();
}
