#include <Servo.h>

// Coin selector - alleen 2-euro munten
// 1 puls = 40 cent → 5 pulsen = €2,00

const int coinSelector    = A0;   // Analog input pin from coin selector
const int pulseThreshold  = 700;  // Drempel voor "hoog" (finetunen indien nodig)

const int pulsesPerCoin   = 5;    // 5 pulsen per munt
const int sensorPin       = 13;   // signaal naar Mega sensor 5
const int servoPin        = 9;    // servo op D9

// Variabelen
int signalValue  = 0;
int state        = 0;
int lastState    = 0;

unsigned long lastPulseTime   = 0;
const unsigned long pulseDebounceMs = 40;  // min. tijd tussen twee geldige pulsen

long totalPulses = 0;   // totaal aantal pulsen ooit
long coinCount   = 0;   // aantal 2-euro munten

bool servoActivated = false;     // 2 munten gezien?
bool servoDetached  = false;     // servo al losgekoppeld?
unsigned long servoMoveTime = 0; // tijdstip dat servo bewoog

Servo myServo;

void setup() {
  pinMode(sensorPin, OUTPUT);
  digitalWrite(sensorPin, LOW); // sensor signaal LOW bij start
  Serial.begin(9600);

  // BIJ ELKE RESET: servo eerst naar uitgangspositie (0 graden)
  myServo.attach(servoPin);
  myServo.write(95);       // uitgangspositie
  delay(500);             // even de tijd geven om daar te komen
  myServo.detach();       // loskoppelen -> geen brommen

  servoActivated = false;
  servoDetached  = false;

  delay(2000);  // coin selector laten opstarten
  Serial.println("Ready..");
}

void loop() {
  // 1. Lees analoge waarde
  signalValue = analogRead(coinSelector);

  // 2. Drempel → 0/1 signaal
  state = (signalValue > pulseThreshold) ? 1 : 0;

  // 3. Detecteer rising edge (0 -> 1) = nieuwe puls
  if (state == 1 && lastState == 0) {
    unsigned long now = millis();

    // simpele debouncing
    if (now - lastPulseTime > pulseDebounceMs) {
      lastPulseTime = now;

      totalPulses++;

      // Elke 5 pulsen = 1 munt
      if (totalPulses % pulsesPerCoin == 0) {
        coinCount++;

        Serial.println("Nieuwe munt gedetecteerd!");
        Serial.print("Aantal munten: ");
        Serial.println(coinCount);
        Serial.println("-----");
      }
    }
  }

  // >>> Zodra er 2 munten zijn, servo naar 160 graden <<<
  if (coinCount >= 2 && !servoActivated) {
    Serial.println("2 munten gezien -> servo naar 160 graden!");

    myServo.attach(servoPin);   // nu pas servo aansluiten
    myServo.write(160);         // naar 160°
    servoMoveTime = millis();   // onthoud wanneer hij draaide

    servoActivated = true;
    servoDetached  = false;
  }

  // Na 500 ms servo loskoppelen zodat hij niet blijft brommen
  if (servoActivated && !servoDetached && millis() - servoMoveTime > 500) {
    myServo.detach();
    servoDetached = true;
    Serial.println("Servo losgekoppeld om brommen te voorkomen.");
  }

  // >>> Sensor signaal naar Mega: HIGH bij 3e munt <<<
  if (coinCount >= 3) {
    digitalWrite(sensorPin, HIGH);
  }

  lastState = state;

  delay(1);  // klein beetje rust
}
