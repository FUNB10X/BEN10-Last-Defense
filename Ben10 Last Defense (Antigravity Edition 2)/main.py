"""
Ben 10 Last Defense — root entry point.
Run: python main.py
"""
import os
import sys

# ฟังก์ชันสำหรับหาตำแหน่งไฟล์ทั้งตอนรันปกติและตอน Build
def resource_path(relative_path):
    try:
        # PyInstaller สร้างโฟลเดอร์ชั่วคราวและเก็บ path ไว้ใน _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# เปลี่ยน Directory ไปที่ที่ไฟล์นี้อยู่
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# นำเข้า main จากโฟลเดอร์เกม
from ben10_defense.main import main

if __name__ == '__main__':
    # ถ้าใน main.py ของคุณมีการเรียกใช้ชื่อไฟล์เพลงหรือฟอนต์ตรงๆ
    # ให้เปลี่ยนไปเรียกใช้ผ่าน resource_path("ชื่อไฟล์.mp3") 
    # ในไฟล์ ben10_defense/main.py หรือไฟล์ที่เกี่ยวข้องนะครับ
    main()
