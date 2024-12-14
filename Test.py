import cv2
import face_recognition
import os
import serial

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
                known_face_names.append("Te")    # สำหรับรูปของ Te
            else:
                known_face_names.append("Unknown")  # รูปอื่น ๆ ที่ไม่ตรงตามเงื่อนไข

    return known_face_encodings, known_face_names

# ฟังก์ชั่นในการตรวจสอบใบหน้าจากกล้อง
def recognize_face_from_camera(known_face_encodings, known_face_names, ser):
    cap = cv2.VideoCapture(0)  # เปิดกล้อง (ใช้กล้องตัวแรก)
    if not cap.isOpened():
        print("ไม่สามารถเปิดกล้องได้")
        return

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

        if len(face_locations) == 0:
            # หากไม่พบใบหน้า
            print("ไม่พบใบหน้า")
            recognized_name = "ไม่พบใบหน้า"
            # ส่งคำสั่งไปยัง Arduino ปิดประตู
            ser.write(b"0")
        else:
            face_recognized = False  # ตัวแปรเพื่อตรวจสอบว่าเจอใบหน้าที่รู้จักหรือไม่
            recognized_name = "ไม่รู้จักใบหน้านี้"  # กำหนดชื่อเริ่มต้นเป็น "ไม่รู้จักใบหน้านี้"

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                # เปรียบเทียบใบหน้าในภาพกับใบหน้าที่รู้จัก
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)

                # ถ้ามีการจับคู่ที่สำเร็จ
                if True in matches:
                    first_match_index = matches.index(True)
                    recognized_name = f"ใบหน้านี้คือ: {known_face_names[first_match_index]}"  # แสดงชื่อที่รู้จัก
                    face_recognized = True

            if face_recognized:
                print(recognized_name)
                # ส่งคำสั่งไปยัง Arduino เปิดประตู
                ser.write(b"1")
            else:
                print(recognized_name)
                # ส่งคำสั่งไปยัง Arduino ปิดประตู
                ser.write(b"0")

        # วาดกรอบรอบใบหน้า
        for (top, right, bottom, left) in face_locations:
            # คูณตำแหน่งใบหน้ากลับเพื่อให้ตรงกับขนาดภาพต้นฉบับ
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # วาดกรอบรอบใบหน้าในภาพ
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # แสดงภาพที่ได้จากกล้อง
        cv2.imshow("Face Recognition", frame)

        # หยุดการจับภาพเมื่อกด 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# เชื่อมต่อกับ Arduino
ser = serial.Serial('COM8', 9600)  # ตรวจสอบ COM port ของ Arduino
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

# โหลดข้อมูลใบหน้าจากรูปภาพ
known_face_encodings, known_face_names = load_face_data(image_paths)

# ทดสอบการจดจำใบหน้าจากกล้อง
recognize_face_from_camera(known_face_encodings, known_face_names, ser)
