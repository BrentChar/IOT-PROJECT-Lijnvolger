// ==== MOTOR PINS (aangesloten op gereserveerde pinnen) ====
const int ENA = 11;  // PWM (normaal SPI-flash)
const int IN1 = 6;   // Gereserveerd (SPI-flash CLK)
const int IN2 = 7;   // Gereserveerd (SPI-flash SD0)
const int ENB = 10;  // PWM (normaal SPI-flash)
const int IN3 = 8;   // Gereserveerd (SPI-flash SD1)
const int IN4 = 15;  // Veilig (geen probleem)

// ==== PWM CONFIG ====
const int Motor_Left_Channel = 0;
const int Motor_Right_Channel = 1;
const int Test_Speed = 180;

void setup() {
  // Alleen IN4 is veilig om te initialiseren
  pinMode(IN4, OUTPUT);
  digitalWrite(IN4, LOW);

  // PWM voor ENA/ENB (kan werken als SPI niet actief is)
  ledcSetup(Motor_Left_Channel, 1000, 8);
  ledcSetup(Motor_Right_Channel, 1000, 8);
  ledcAttachPin(ENB, Motor_Left_Channel);
  ledcAttachPin(ENA, Motor_Right_Channel);
  ledcWrite(Motor_Left_Channel, 0);
  ledcWrite(Motor_Right_Channel, 0);

  Serial.begin(115200);
  Serial.println("Motor test (RISICO: SPI-flash conflicten!)");
}

void loop() {
  // ==== MOTOR AANSTUREN (alleen tijdens loop, niet tijdens boot) ====
  // - SPI-flash wordt alleen gebruikt tijdens opstarten en bij firmware-uploads
  // - Tijdens `loop()` kunnen we *voorzichtig* pinnen 6-11 gebruiken

  // Rechter motor vooruit (IN1=HIGH, IN2=LOW)
  pinMode(IN1, OUTPUT);  // RISICO: SPI CLK wordt overschreven
  pinMode(IN2, OUTPUT);  // RISICO: SPI SD0 wordt overschreven
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  ledcWrite(Motor_Right_Channel, Test_Speed);

  // Linker motor uit (IN3/IN4)
  pinMode(IN3, OUTPUT);  // RISICO: SPI SD1 wordt overschreven
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  ledcWrite(Motor_Left_Channel, 0);

  delay(2000);

  // Motoren uitzetten
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  ledcWrite(Motor_Right_Channel, 0);
  delay(2000);
}