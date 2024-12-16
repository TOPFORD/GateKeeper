import serial
import cv2
import face_recognition
import os
import time

# ตั้งค่าพอร์ต Serial ที่เชื่อมต่อกับ Arduino UNO
ser = serial.Serial('COM9', 9600)  # เปลี่ยน 'COM8' ให้ตรงกับพอร์ตที่เชื่อมต่อ
ser.flushInput()

# ฟังก์ชั่นในการโหลดข้อมูลใบหน้าและเก็บ face encoding
def load_face_data(image_paths):
    known_face_encodings = []
    known_face_names = []

    for image_path in image_paths:
        if not os.path.exists(image_path):
            print(f"ไม่สามารถโหลดไฟล์: {image_path}")
            continue

        image = cv2.imread(image_path)
        if image is None:
            print(f"ไม่สามารถโหลดภาพจากไฟล์: {image_path}")
            continue

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        for encoding in face_encodings:
            known_face_encodings.append(encoding)
            if os.path.basename(image_path).startswith("Ford"):
                known_face_names.append("Ford")
            elif os.path.basename(image_path).startswith("t"):
                known_face_names.append("Te")
            else:
                known_face_names.append("Unknown")

    return known_face_encodings, known_face_names

# ฟังก์ชั่นในการตรวจสอบใบหน้าจากกล้อง
def recognize_face_from_camera(known_face_encodings, known_face_names):
    cap = cv2.VideoCapture(0)  # เปิดกล้อง

    while True:
        ret, frame = cap.read()  # อ่านภาพจากกล้อง
        if not ret:
            print("ไม่สามารถดึงภาพจากกล้องได้.")
            break

        if ser.in_waiting > 0:
            try:
                raw_data = ser.readline().decode('utf-8').strip()  # อ่านข้อมูลดิบจาก Serial
                print(f"Raw data: {raw_data}")  # แสดงข้อมูลดิบเพื่อ Debug
                
                # ตรวจสอบว่าข้อมูลมีคำว่า "Distance:" หรือไม่
                if "Distance:" in raw_data:
                    # แยกเฉพาะตัวเลขจากข้อความ
                    distance_str = raw_data.split("Distance:")[-1].strip()
                    distance = float(distance_str)  # แปลงตัวเลขจากข้อความเป็น float
                    print(f"Distance: {distance} cm")

                    if distance <= 5:
                        ser.write(b"0")  # ส่งคำสั่งปิดประตู
                        time.sleep(5)
                        ser.write(b"0")  # ส่งคำสั่งปิดประตูซ้ำ
                else:
                    print("ข้อมูลไม่มีคำว่า 'Distance:'")
            except ValueError:
                print(f"ไม่สามารถแปลงข้อมูลได้: {raw_data}")
            except Exception as e:
                print(f"ข้อผิดพลาด: {e}")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                ser.write(b"0")
                time.sleep(5)
                ser.write(b"1")
                print("เปิด")

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# โหลดข้อมูลใบหน้าจากหลายๆ รูป
image_paths = [
    'Ford1.jpg',
    'Ford2.jpg',
    'Ford3.jpg',
    'Ford4.jpg',
    'Ford5.jpg',
    'Ford6.jpg',
    'Ford7.jpg',
    'Ford8.jpg',
    'Ford9.jpg',
    'Ford10.jpg',
    't1.jpg',
    't2.jpg',
    't3.jpg',
    't4.jpg',
    't5.jpg'
]
known_face_encodings, known_face_names = load_face_data(image_paths)

# เริ่มการจดจำใบหน้าจากกล้อง
recognize_face_from_camera(known_face_encodings, known_face_names)
