#include <DHT.h>
#include <SoftwareSerial.h>

// --- CONFIGURAÇÃO ---
#define DHTPIN 2     // Sensor de Dados
#define GNDPIN 9     // Terra Virtual do Sensor
#define DHTTYPE DHT22

// --- BLUETOOTH (SoftwareSerial) ---
// Arduino RX (Recebe) vai no TX do Bluetooth (Pino 10)
// Arduino TX (Envia) vai no RX do Bluetooth (Pino 11)
SoftwareSerial bluetooth(10, 11); // RX, TX

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  // Serial do USB (Para Debug no PC se precisar)
  Serial.begin(9600);
  
  // Serial do Bluetooth
  bluetooth.begin(9600);
  
  Serial.println("Inicializando...");
  bluetooth.println("Inicializando via Bluetooth...");

  // --- CONFIGURA TERRA VIRTUAL (Pino 9) ---
  pinMode(GNDPIN, OUTPUT);
  digitalWrite(GNDPIN, LOW); // Transforma em GND
  
  delay(500); 
  dht.begin();
}

void loop() {
  delay(2000);

  float umidade = dht.readHumidity();
  float temperatura = dht.readTemperature();

  // Se falhar
  if (isnan(umidade) || isnan(temperatura)) {
    String erro = "Erro: Falha na leitura do DHT22!";
    Serial.println(erro);
    bluetooth.println(erro); // Manda pro Bluetooth também
    return;
  }

  // --- FORMATAÇÃO PRO PYTHON ---
  // Formato: "Temp: 25.00 | Umid: 65.00"
  String mensagem = "Temp: " + String(temperatura) + " | Umid: " + String(umidade);
  
  // Manda para o USB e para o Bluetooth
  Serial.println(mensagem);      
  bluetooth.println(mensagem);
}
