import cv2
import face_recognition
import os
import numpy as np
import pickle
import serial
import time

# ตั้งค่าพอร์ต Serial ที่เชื่อมต่อกับ Arduino UNO
try:
    ser = serial.Serial('COM9', 9600, timeout=1)
    ser.flushInput()
    print("เชื่อมต่อ Serial สำเร็จ")
except Exception as e:
    print(f"ไม่สามารถเชื่อมต่อ Serial: {e}")
    ser = None

# ฟังก์ชั่นในการโหลดหลายรูปภาพและเก็บ face encoding
def load_face_data(image_paths):
    known_face_encodings = []
    known_face_names = []

    for image_path in image_paths:
        # ตรวจสอบว่าไฟล์รูปภาพสามารถโหลดได้หรือไม่
        if not os.path.exists(image_path):
            print(f"ไม่สามารถโหลดไฟล์: {image_path}")
            continue

        # โหลดรูปภาพ
        image = cv2.imread(image_path)

        if image is None:
            print(f"ไม่สามารถโหลดภาพจากไฟล์: {image_path}")
            continue

        # แปลงรูปภาพเป็น RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # หาตำแหน่งใบหน้าและ encode ใบหน้า
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        for encoding in face_encodings:
            known_face_encodings.append(encoding)

            # กำหนดชื่อสำหรับใบหน้า
            if os.path.basename(image_path).startswith("Ford"):
                known_face_names.append("Ford")  # สำหรับรูปของ Ford
            elif os.path.basename(image_path).startswith("t"):
                known_face_names.append("tae")    # สำหรับรูปของ Te
            elif os.path.basename(image_path).startswith("g"):
                known_face_names.append("gg")    # สำหรับรูปของ gg
            elif os.path.basename(image_path).startswith("j"):
                known_face_names.append("jj")    # สำหรับรูปของ jj
            else:
                known_face_names.append("Unknown")  # รูปอื่น ๆ ที่ไม่ตรงตามเงื่อนไข

    return known_face_encodings, known_face_names

# ฟังก์ชั่นในการตรวจสอบใบหน้าจากกล้อง
def recognize_face_from_camera(known_face_encodings, known_face_names):
    cap = cv2.VideoCapture(0)  # เปิดกล้อง (ใช้กล้องตัวแรก)
    TOLERANCE = 0.4  # ความเคร่งครัดในการจับคู่
    if not cap.isOpened():
        print("ไม่สามารถเปิดกล้องได้")
        return

    try:
        while True:
            ret, frame = cap.read()  # อ่านภาพจากกล้อง
            if not ret:
                print("ไม่สามารถดึงภาพจากกล้องได้.")
                break

            # ลดขนาดภาพเพื่อลดเวลาในการประมวลผล
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # หาตำแหน่งใบหน้าในภาพ
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # เปรียบเทียบใบหน้าในภาพกับใบหน้าที่รู้จัก
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=TOLERANCE)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                name = "Unknown"  # ตั้งค่าเริ่มต้นเป็น Unknown

                # ถ้ามีการจับคู่ที่สำเร็จ เลือกใบหน้าที่ใกล้เคียงที่สุด
                if len(face_distances) > 0 and matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                        # สั่งเปิดประตูผ่าน Serial หากเป็นบุคคลที่รู้จัก
                        if ser:
                            ser.write(b"0")
                            time.sleep(5)
                            ser.write(b"1")
                            print("เปิด")

                # คูณตำแหน่งใบหน้ากลับเพื่อให้ตรงกับขนาดภาพต้นฉบับ
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # ตั้งสีกรอบและข้อความ
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)

                # วาดกรอบรอบใบหน้าและชื่อ
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            # แสดงภาพที่ได้จากกล้อง
            cv2.imshow("Face Recognition", frame)

            # อ่านข้อมูลจาก Serial (ตรวจสอบระยะทาง)
            if ser and ser.in_waiting > 0:
                try:
                    raw_data = ser.readline().decode('utf-8').strip()
                    if "Distance:" in raw_data:
                        distance = float(raw_data.split("Distance:")[-1])
                        print(f"Distance: {distance} cm")
                        if distance <= 5:
                            ser.write(b"0")  # ปิดประตูหากมีวัตถุใกล้
                            # time.sleep(5)
                except Exception as e:
                    print(f"ข้อผิดพลาดในการอ่าน Serial: {e}")

            # หยุดการจับภาพเมื่อกด 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        if ser:
            ser.close()

# รายชื่อไฟล์ภาพ
image_paths = [
    'Ford1.jpg',  # รูปแรกของคุณ (Ford)
    'Ford2.jpg',  # รูปที่สองของคุณ (Ford)
    'Ford3.jpg',  # รูปที่สามของคุณ (Ford)
    'Ford4.jpg',
    'Ford5.jpg',
    'Ford6.jpg',
    'Ford7.jpg',
    'Ford8.jpg',
    'Ford9.jpg',
    'Ford10.jpg',
    't1.jpg',     # รูปแรกของ Te
    't2.jpg',     # รูปที่สองของ Te
    't3.jpg',     # รูปที่สามของ Te
    't4.jpg',     # รูปที่สี่ของ Te
    't5.jpg' ,     # รูปที่ห้าของ Te
    't6.jpg' , 
    't7.jpg'  ,
    't8.jpg'  ,
    't9.jpg'  ,
    't10.jpg'  ,
    'g1.jpg' ,  
    'g2.jpg' , 
    'g3.jpg' , 
    'g4.jpg' , 
    'g5.jpg' , 
    'g6.jpg' , 
    'g7.jpg' , 
    'g8.jpg'  , 
    'j1.jpg'  , 
    'j2.jpg'  ,
    'j3.jpg',
    'j4.jpg',
    'j5.jpg',
    'j6.jpg',
    'j7.jpg',
    'j8.jpg',
    'j9.jpg'
]

# ถ้ามีไฟล์ pickle ใช้ข้อมูลเดิม ไม่ต้องโหลดใหม่
if os.path.exists('face_data.pkl'):
    with open('face_data.pkl', 'rb') as f:
        known_face_encodings, known_face_names = pickle.load(f)
else:
    # โหลดข้อมูลใบหน้าใหม่
    known_face_encodings, known_face_names = load_face_data(image_paths)
    # บันทึกข้อมูลเพื่อใช้ในอนาคต
    with open('face_data.pkl', 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)

# ทดสอบการจดจำใบหน้าจากกล้อง
recognize_face_from_camera(known_face_encodings, known_face_names)
