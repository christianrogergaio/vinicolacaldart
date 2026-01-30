#include <DHT.h>

// --- CONFIGURAÇÃO ESPECIAL ---
#define DHTPIN 2     // Dados no pino 2
#define GNDPIN 9     // Onde você ligou o terceiro fio (Vamos transformar em Negativo)
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.println("Inicializando com Terra Virtual no pino 9...");

  // --- TRUQUE DO "TERRA VIRTUAL" ---
  // Transforma o pino 9 em um "Negativo" (GND) para não precisar ressoldar
  pinMode(GNDPIN, OUTPUT);
  digitalWrite(GNDPIN, LOW); // LOW = 0V = GND
  
  delay(500); // Dá um tempo pro sensor ligar com a nova energia
  dht.begin();
}

void loop() {
  delay(2000);

  float umidade = dht.readHumidity();
  float temperatura = dht.readTemperature();

  // Verifica se houve falha na leitura
  if (isnan(umidade) || isnan(temperatura)) {
    Serial.println("Erro: Sensor DHT22 nao detectado!");
    Serial.print("Verifique se o fio do TERRA esta mesmo no pino ");
    Serial.println(GNDPIN);
    return;
  }

  // Formato esperado pelo seu Python: "Temp: 25.00 | Umid: 65.00"
  Serial.print("Temp: ");
  Serial.print(temperatura);
  Serial.print(" | Umid: ");
  Serial.println(umidade);
}
