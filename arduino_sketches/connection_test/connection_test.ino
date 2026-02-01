#include <WiFi.h>
#include <WiFiClientSecure.h>

const char* ssid = "VALQUIRIA_2G";
const char* password = "sergio-gio";

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n--- DIAGNOSTICO DE REDE ESP32 ---");

  // 1. CONEXÃO WIFI
  Serial.print("1. Conectando ao WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n   WiFi CONECTADO!");
    Serial.print("   IP: "); Serial.println(WiFi.localIP());
    Serial.print("   Gateway: "); Serial.println(WiFi.gatewayIP());
    Serial.print("   DNS: "); Serial.println(WiFi.dnsIP());
  } else {
    Serial.println("\n   ERRO: Falha ao conectar no WiFi. Verifique senha ou alcance.");
    return; // Para por aqui
  }

  // 2. TESTE GOOGLE (HTTP - Porta 80)
  Serial.println("\n2. Teste Google HTTP (Porta 80)...");
  WiFiClient clientHttp;
  if(clientHttp.connect("www.google.com", 80)) {
     Serial.println("   SUCESSO! Internet funcionando (HTTP basico).");
     clientHttp.stop();
  } else {
     Serial.println("   FALHA! Nao conectou ao Google na porta 80.");
  }

  // 3. TESTE GOOGLE (HTTPS - Porta 443)
  Serial.println("\n3. Teste Google HTTPS (Porta 443)...");
  WiFiClientSecure clientHttps;
  clientHttps.setInsecure(); // Ignora cert
  if(clientHttps.connect("www.google.com", 443)) {
     Serial.println("   SUCESSO! SSL/HTTPS funcionando (Google).");
     clientHttps.stop();
  } else {
     Serial.println("   FALHA! Nao conectou ao Google na porta 443 (Bloqueio ou Erro SSL).");
  }

  // 4. TESTE RENDER (HTTPS - Porta 443)
  Serial.println("\n4. Teste RENDER (Seu Site)...");
  WiFiClientSecure clientRender;
  clientRender.setInsecure();
  const char* host = "vinicolacaldart.onrender.com";
  
  Serial.print("   Resolvendo IP... ");
  IPAddress ip;
  if(WiFi.hostByName(host, ip)) {
    Serial.println(ip);
  } else {
    Serial.println("FALHA DNS!");
  }

  if(clientRender.connect(host, 443)) {
     Serial.println("   SUCESSO! Conectado ao Render!");
     clientRender.println("GET /health HTTP/1.1");
     clientRender.print("Host: "); clientRender.println(host);
     clientRender.println("Connection: close");
     clientRender.println();
     
     while(clientRender.connected()) {
       String line = clientRender.readStringUntil('\n');
       if(line == "\r") break;
     }
     String line = clientRender.readStringUntil('\n');
     Serial.println("   Resposta inicial: " + line);
     clientRender.stop();
  } else {
     Serial.println("   FALHA! Nao conectou ao Render (Connection Refused/Handshake).");
  }
}

void loop() {
  // Nada
}
