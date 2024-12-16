#include <Servo.h>

#define echoPin 4   // ขา Echo ของ HC-SR04
#define trigPin 5   // ขา Trigger ของ HC-SR04

#define echoPin2 6  // ขา Echo ของ HC-SR04
#define trigPin2 7  // ขา Trigger ของ HC-SR04

Servo servo1;  // สร้างออบเจกต์ Servo
Servo servo2;  // สร้างออบเจกต์ Servo

const int servoPin1 = 9;   // ขาที่เชื่อมต่อ Servo1
const int servoPin2 = 10;  // ขาที่เชื่อมต่อ Servo2

long duration;
int distance;

long duration1;
int distance1;

void setup() {
  servo1.attach(servoPin1);  // กำหนดขาให้ Servo1
  servo2.attach(servoPin2);  // กำหนดขาให้ Servo2
  
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);

  servo1.write(0);  // เริ่มต้น Servo1 ที่ตำแหน่ง 0 องศา
  servo2.write(0);  // เริ่มต้น Servo2 ที่ตำแหน่ง 0 องศา
  
  Serial.begin(9600);  // เริ่มต้น Serial communication
}

void loop() {
  // เซ็นเซอร์ตัวแรก
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.0344 / 2;

  Serial.print("Distance: ");
  Serial.println(distance);

  // เซ็นเซอร์ตัวที่สอง
  digitalWrite(trigPin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin2, LOW);

  duration1 = pulseIn(echoPin2, HIGH);
  distance1 = duration1 * 0.0344 / 2;

  // แสดงค่าระยะทาง
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.print(" cm");

  // เงื่อนไขควบคุม Servo2
  if (distance > 5 && distance < 8) {
    servo2.write(60);  // เปิด
  } else if (distance1 <= 5) {
    servo2.write(0);   // ปิด
  }

  // ตรวจสอบคำสั่งจาก Serial
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    if (command == "1") {
      servo1.write(60);  // เปิดประตู
    } else if (command == "0") {
      servo1.write(0);   // ปิดประตู
    }
  }

  // เงื่อนไขควบคุม Servo1 อัตโนมัติ
  if (distance < 5) {
    servo1.write(0);  // ปิดประตู
  }

  delay(500);  // หน่วงเวลา 500ms
}
