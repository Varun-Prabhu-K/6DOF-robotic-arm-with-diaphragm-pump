#include <SoftwareWire.h>

SoftwareWire myWire(2, 3);

#define PCA9685_ADDR 0x40

#define MODE1 0x00
#define MODE2 0x01
#define PRESCALE 0xFE
#define LED0_ON_L 0x06

#define SERVOMIN 110
#define SERVOMAX 500

#define PUMP_PIN 8

#define NUM_JOINTS 6

#define MOVE_DELAY 25

const int HOME_ANGLES[NUM_JOINTS] = {
  90,
  90,
  90,
  90,
  90,
  90
};

int currentAngles[NUM_JOINTS] = {
  90,
  90,
  90,
  90,
  90,
  90
};

String inputBuffer = "";

void writeRegister(uint8_t reg, uint8_t value) {

  myWire.beginTransmission(PCA9685_ADDR);
  myWire.write(reg);
  myWire.write(value);
  myWire.endTransmission();
}

void setPWM(uint8_t channel, uint16_t onValue, uint16_t offValue) {

  if (channel >= 16) {
    return;
  }

  myWire.beginTransmission(PCA9685_ADDR);

  myWire.write(LED0_ON_L + (4 * channel));

  myWire.write(onValue & 0xFF);
  myWire.write((onValue >> 8) & 0x0F);

  myWire.write(offValue & 0xFF);
  myWire.write((offValue >> 8) & 0x0F);

  myWire.endTransmission();
}

void setupPCA9685() {

  writeRegister(MODE1, 0x10);

  delay(10);

  uint8_t prescale =
    (uint8_t)((25000000.0 / (4096.0 * 50.0)) - 0.5);

  writeRegister(PRESCALE, prescale);

  writeRegister(MODE1, 0x00);

  delay(10);

  writeRegister(MODE2, 0x04);

  writeRegister(MODE1, 0xA1);

  delay(10);
}

void setServoAngle(uint8_t channel, int angle) {

  if (channel >= NUM_JOINTS) {
    return;
  }

  angle = constrain(angle, 0, 180);

  int pulse = map(
    angle,
    0,
    180,
    SERVOMIN,
    SERVOMAX
  );

  setPWM(channel, 0, pulse);
}

void moveServoSlow(uint8_t channel, int target) {

  if (channel >= NUM_JOINTS) {
    return;
  }

  target = constrain(target, 0, 180);

  int current = currentAngles[channel];

  if (current == target) {
    setServoAngle(channel, target);
    return;
  }

  while (current != target) {

    if (target > current) {
      current++;
    } else {
      current--;
    }

    setServoAngle(channel, current);

    currentAngles[channel] = current;

    delay(MOVE_DELAY);
  }

  setServoAngle(channel, target);
}

void moveRelative(uint8_t channel, int delta) {

  if (channel >= NUM_JOINTS) {
    return;
  }

  int oldAngle = currentAngles[channel];

  int targetAngle = oldAngle + delta;

  targetAngle = constrain(targetAngle, 0, 180);

  Serial.print("CHANNEL ");
  Serial.print(channel);
  Serial.print(" : ");
  Serial.print(oldAngle);
  Serial.print(" -> ");
  Serial.println(targetAngle);

  moveServoSlow(channel, targetAngle);

  Serial.print("CURRENT = ");
  Serial.print(currentAngles[channel]);
  Serial.println(" deg");
}

void moveAbsolute(uint8_t channel, int angle) {

  if (channel >= NUM_JOINTS) {
    return;
  }

  angle = constrain(angle, 0, 180);

  Serial.print("CHANNEL ");
  Serial.print(channel);
  Serial.print(" : ");
  Serial.print(currentAngles[channel]);
  Serial.print(" -> ");
  Serial.println(angle);

  moveServoSlow(channel, angle);

  Serial.print("CURRENT = ");
  Serial.print(currentAngles[channel]);
  Serial.println(" deg");
}

void goHome() {

  Serial.println("GOING TO HOME POSITION");

  for (int ch = 0; ch < NUM_JOINTS; ch++) {

    moveServoSlow(ch, HOME_ANGLES[ch]);

  }

  Serial.println("HOME POSITION REACHED");
}

void centerAll() {

  Serial.println("CENTERING ALL SERVOS");

  for (int ch = 0; ch < NUM_JOINTS; ch++) {

    moveServoSlow(ch, 90);

  }

  Serial.println("ALL SERVOS AT 90 DEGREES");
}

void pumpOn() {

  digitalWrite(PUMP_PIN, HIGH);

  Serial.println("PUMP ON");
}

void pumpOff() {

  digitalWrite(PUMP_PIN, LOW);

  Serial.println("PUMP OFF");
}

bool isInteger(String value) {

  value.trim();

  if (value.length() == 0) {
    return false;
  }

  int start = 0;

  if (
    value.charAt(0) == '+' ||
    value.charAt(0) == '-'
  ) {
    start = 1;
  }

  if (start >= value.length()) {
    return false;
  }

  for (int i = start; i < value.length(); i++) {

    if (!isDigit(value.charAt(i))) {
      return false;
    }
  }

  return true;
}

void printHelp() {

  Serial.println();
  Serial.println("================================");
  Serial.println("       ROBOTIC ARM READY");
  Serial.println("================================");

  Serial.println();
  Serial.println("RELATIVE MOVEMENT");
  Serial.println("0 5       Channel 0 +5 deg");
  Serial.println("0 -5      Channel 0 -5 deg");
  Serial.println("1 5       Channel 1 +5 deg");
  Serial.println("1 -5      Channel 1 -5 deg");

  Serial.println();
  Serial.println("ABSOLUTE MOVEMENT");
  Serial.println("0 =90     Channel 0 -> 90 deg");
  Serial.println("2 =90     Channel 2 -> 90 deg");

  Serial.println();
  Serial.println("HOME");
  Serial.println("c         Home position");
  Serial.println("home      Home position");

  Serial.println();
  Serial.println("PUMP");
  Serial.println("on        Pump ON");
  Serial.println("off       Pump OFF");

  Serial.println();
  Serial.println("CHANNEL MAPPING");
  Serial.println("0 = J4");
  Serial.println("1 = J0");
  Serial.println("2 = J1");
  Serial.println("3 = J6");
  Serial.println("4 = J3");
  Serial.println("5 = J5");

  Serial.println();
  Serial.println("HOME ANGLES");
  Serial.println("J4 = 90");
  Serial.println("J0 = 90");
  Serial.println("J1 = 90");
  Serial.println("J6 = 90");
  Serial.println("J3 = 90");
  Serial.println("J5 = 90");

  Serial.println();
}

void processCommand(String command) {

  command.trim();

  if (command.length() == 0) {
    return;
  }

  while (command.indexOf("  ") >= 0) {
    command.replace("  ", " ");
  }

  if (command.equalsIgnoreCase("h")) {

    printHelp();

    return;
  }

  if (command.equalsIgnoreCase("c")) {

    centerAll();

    return;
  }

  if (command.equalsIgnoreCase("home")) {

    goHome();

    return;
  }

  if (command.equalsIgnoreCase("on")) {

    pumpOn();

    return;
  }

  if (command.equalsIgnoreCase("off")) {

    pumpOff();

    return;
  }

  int space = command.indexOf(' ');

  if (space <= 0) {

    Serial.println("ERROR: use <channel> <value>");

    return;
  }

  String channelText =
    command.substring(0, space);

  String valueText =
    command.substring(space + 1);

  channelText.trim();
  valueText.trim();

  if (!isInteger(channelText)) {

    Serial.println("ERROR: invalid channel");

    return;
  }

  int channel = channelText.toInt();

  if (
    channel < 0 ||
    channel >= NUM_JOINTS
  ) {

    Serial.println("ERROR: channel must be 0-5");

    return;
  }

  if (valueText.startsWith("=")) {

    String angleText =
      valueText.substring(1);

    angleText.trim();

    if (!isInteger(angleText)) {

      Serial.println("ERROR: invalid absolute angle");

      return;
    }

    int angle = angleText.toInt();

    if (
      angle < 0 ||
      angle > 180
    ) {

      Serial.println("ERROR: angle must be 0-180");

      return;
    }

    moveAbsolute(channel, angle);

    return;
  }

  if (!isInteger(valueText)) {

    Serial.println("ERROR: invalid movement");

    return;
  }

  int delta = valueText.toInt();

  moveRelative(channel, delta);
}

void setup() {

  Serial.begin(9600);

  delay(1000);

  myWire.begin();

  delay(100);

  pinMode(PUMP_PIN, OUTPUT);

  digitalWrite(PUMP_PIN, LOW);

  setupPCA9685();

  delay(100);

  for (int ch = 0; ch < NUM_JOINTS; ch++) {

    setServoAngle(ch, 90);

    currentAngles[ch] = 90;

    delay(100);
  }

  delay(1000);

  printHelp();
}

void loop() {

  while (Serial.available() > 0) {

    char c = Serial.read();

    if (
      c == '\n' ||
      c == '\r'
    ) {

      if (inputBuffer.length() > 0) {

        processCommand(inputBuffer);

        inputBuffer = "";
      }

    } else {

      if (inputBuffer.length() < 50) {

        inputBuffer += c;
      }
    }
  }
}
