import serial

ser = serial.Serial('COM8', 9600)  # ตั้งค่าพอร์ตและ Baud Rate ให้ตรงกับ Arduino
ser.flushInput()

while True:
    try:
        if ser.in_waiting > 0:  # ตรวจสอบว่ามีข้อมูลใน Serial Buffer
            data = ser.readline().decode('utf-8').strip()  # อ่านข้อมูล, แปลง, และลบ '\n' หรือ '\r'
            print(f"Raw data: {data}")  # แสดงข้อมูลดิบเพื่อ debug
            
            distance = float(data)  # แปลงข้อมูลเป็น float
            print(f"Distance: {distance} cm")  # แสดงระยะทางที่แปลงสำเร็จ
    except ValueError:
        print(f"ไม่สามารถแปลงข้อมูลได้: {data}")  # แสดงข้อผิดพลาดถ้าแปลงข้อมูลไม่ได้
    except Exception as e:
        print(f"ข้อผิดพลาด: {e}")  # แสดงข้อผิดพลาดอื่น ๆ
