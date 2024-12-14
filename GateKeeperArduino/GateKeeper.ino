#include <Servo.h>

#define echoPin 4   // ขา Echo ของ HC-SR04
#define trigPin 5   // ขา Trigger ของ HC-SR04
Servo servo;  // สร้างออบเจกต์ Servo

const int servoPin = 9; // ขาที่เชื่อมต่อ Servo

long duration;
int distance;

void setup() {
  servo.attach(servoPin); // กำหนดขาให้ Servo
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  servo.write(0);  // เริ่มต้น Servo ที่ตำแหน่ง 0 องศา
  Serial.begin(9600); // เริ่มต้น Serial communication
}

void loop() {
  digitalWrite(trigPin, LOW);  // ตั้งให้ Trigger เป็น LOW
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); // ตั้งให้ Trigger เป็น HIGH
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);  // ตั้งให้ Trigger เป็น LOW

  duration = pulseIn(echoPin, HIGH);

  // คำนวณระยะทางจากเวลาที่ได้
  distance = duration * 0.0344 / 2;  // ความเร็วเสียง 0.0344 cm/us
//
  Serial.print("Distance: ");
  Serial.println(distance);
  
  // ตรวจสอบคำสั่งจาก Serial
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n'); // รับคำสั่งจาก Serial

    // ตรวจสอบคำสั่งและหมุนมอเตอร์
    if (command == "1") {
      servo.write(90); // หมุนมอเตอร์ไปที่ 90 องศา
    }
    else if (command == "0"){
      servo.write(0); // หมุนมอเตอร์ไปที่ 0 องศา
    }
  }

  // หากระยะทางน้อยกว่าหรือเท่ากับ 5 ซม. ปิดประตูอัตโนมัติ
  if (distance <= 5) {
    servo.write(0);  // ปิดประตู
  }

  delay(500);  // รอ 500ms ก่อนที่จะอ่านข้อมูลใหม่
}
