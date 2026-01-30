#include "BluetoothSerial.h"

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  
  // Inicia em modo MASTER (true)
  // O nome "ESP32_Scanner" é como ele vai aparecer (irrelevante pois somos master)
  if(!SerialBT.begin("ESP32_Scanner", true)) {
    Serial.println("Erro ao iniciar Bluetooth");
    while(true);
  }
  
  Serial.println("===========================================");
  Serial.println("Iniciando Escaneamento Bluetooth (10 segs)");
  Serial.println("===========================================");

  // Escaneia por 10.000 ms (10s)
  BTScanResults *pResults = SerialBT.discover(10000);
  
  if (pResults) {
    Serial.print("Dispositivos Encontrados: ");
    Serial.println(pResults->getCount());
    Serial.println("-------------------------------------------");
    
    for (int i = 0; i < pResults->getCount(); i++) {
      BTAdvertisedDevice* device = pResults->getDevice(i);
      
      Serial.print("Nome: ");
      Serial.print(device->getName().c_str());
      Serial.print("  |  MAC: ");
      Serial.println(device->getAddress().toString().c_str());
    }
    Serial.println("-------------------------------------------");
    Serial.println("Copie o endereço MAC do seu HC-05!");
  } else {
    Serial.println("Nenhum dispositivo encontrado.");
  }
}

void loop() {
  delay(1000);
}
