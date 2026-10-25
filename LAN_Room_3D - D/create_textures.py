# create_item_textures.py
import os
from PIL import Image, ImageDraw, ImageFilter


def create_base_canvas(size=(300, 300)):
    """สร้างพื้นหลังการ์ด Sci-Fi สีน้ำเงินเข้มพร้อมกรอบเรืองแสง"""
    img = Image.new("RGBA", size, (10, 20, 40, 240))
    draw = ImageDraw.Draw(img)

    # กรอบนอกเรืองแสงสีฟ้า Cyan
    draw.rectangle([10, 10, size[0] - 10, size[1] - 10], outline=(0, 200, 255, 255), width=4)
    draw.rectangle([16, 16, size[0] - 16, size[1] - 16], outline=(0, 100, 180, 150), width=2)

    # เส้นแต่งมุม 4 ด้านสไตล์ Sci-Fi
    corner_len = 25
    # มุมบนซ้าย
    draw.line([(10, 10 + corner_len), (10, 10), (10 + corner_len, 10)], fill=(0, 255, 255), width=6)
    # มุมขวาบน
    draw.line([(size[0] - 10 - corner_len, 10), (size[0] - 10, 10), (size[0] - 10, 10 + corner_len)], fill=(0, 255, 255), width=6)
    # มุมซ้ายล่าง
    draw.line([(10, size[1] - 10 - corner_len), (10, size[1] - 10), (10 + corner_len, size[1] - 10)], fill=(0, 255, 255), width=6)
    # มุมขวาล่าง
    draw.line([(size[0] - 10 - corner_len, size[1] - 10), (size[0] - 10, size[1] - 10), (size[0] - 10, size[1] - 10 - corner_len)], fill=(0, 255, 255), width=6)

    return img, draw


def generate_all_equipment_textures():
    output_dir = "textures/items"
    os.makedirs(output_dir, exist_ok=True)
    print("⏳ กำลังวาดและสร้างรูปภาพอุปกรณ์สำหรับเกม LAN Lab...")

    # -------------------------------------------------------------
    # 1. รูปสาย UTP (ขดสายสีฟ้า Cat6 พร้อมหัวสาย)
    # -------------------------------------------------------------
    img, draw = create_base_canvas()
    # ขดสายชั้นนอก
    draw.ellipse([50, 50, 250, 250], outline=(0, 120, 240, 255), width=28)
    draw.ellipse([75, 75, 225, 225], outline=(0, 80, 180, 255), width=20)
    # สายพาดเฉียง
    draw.line([(40, 220), (120, 140)], fill=(0, 140, 255), width=18)
    # ปลายสายปอกเปลือก (แสดงสายไฟเล็กๆ 4 คู่)
    wire_colors = [(255, 140, 0), (0, 120, 255), (0, 200, 80), (160, 90, 40)]
    for i, col in enumerate(wire_colors):
        draw.line([(120 + i*6, 140 - i*6), (150 + i*8, 110 - i*8)], fill=col, width=4)

    img.save(os.path.join(output_dir, "utp.png"))

    # -------------------------------------------------------------
    # 2. รูปหัว RJ45 (หัวคอนเนกเตอร์ใส พร้อม Pin ทองเหลือง 8 พิน)
    # -------------------------------------------------------------
    img, draw = create_base_canvas()
    # บล็อกหัวพลาสติกใสโปร่งแสง
    draw.rectangle([70, 70, 230, 230], fill=(160, 210, 255, 160), outline=(220, 245, 255, 255), width=4)
    # คลิปสลักล็อกด้านบน
    draw.rectangle([120, 40, 180, 75], fill=(180, 225, 255, 200), outline=(255, 255, 255), width=3)
    # พินทองเหลือง 8 ช่อง (Gold Pins 1-8)
    for i in range(8):
        x = 85 + (i * 17)
        draw.rectangle([x, 80, x + 10, 140], fill=(255, 200, 40), outline=(180, 130, 10), width=1)
    # ล็อคสายก้นหัว
    draw.rectangle([90, 190, 210, 220], fill=(100, 140, 180, 220))

    img.save(os.path.join(output_dir, "rj45.png"))

    # -------------------------------------------------------------
    # 3. รูปคีมย้ำ RJ45 (Crimping Tool ด้ามสีส้ม-เทา)
    # -------------------------------------------------------------
    img, draw = create_base_canvas()
    # หัวคีมโลหะเหล็ก
    draw.rectangle([90, 40, 210, 120], fill=(120, 130, 140), outline=(200, 210, 220), width=3)
    draw.rectangle([110, 60, 190, 100], fill=(40, 50, 60))  # ช่องย้ำ RJ45
    # ด้ามจับคู่สีส้มสด
    draw.rectangle([80, 130, 125, 265], fill=(255, 100, 0), outline=(30, 30, 30), width=3)
    draw.rectangle([175, 130, 220, 265], fill=(255, 100, 0), outline=(30, 30, 30), width=3)
    # ข้อต่อหมุดสลักหมุน
    draw.ellipse([135, 120, 165, 150], fill=(200, 200, 200), outline=(50, 50, 50), width=2)

    img.save(os.path.join(output_dir, "crimper.png"))

    # -------------------------------------------------------------
    # 4. รูป Cable Tester (เครื่องวัดสัญญาณสาย LAN มีไฟ LED 1-8)
    # -------------------------------------------------------------
    img, draw = create_base_canvas()
    # ตัวเครื่องหลัก (Master Unit)
    draw.rectangle([50, 40, 170, 260], fill=(30, 160, 90), outline=(220, 255, 220), width=4)
    # เครื่องแยกส่งสัญญาณ (Remote Unit)
    draw.rectangle([185, 40, 250, 260], fill=(25, 140, 80), outline=(200, 240, 200), width=3)

    # หลอดไฟ LED แสดงสถานะ Pin 1-8 (สีเขียวเรืองแสง)
    for i in range(8):
        y = 65 + (i * 22)
        # ไฟบน Master
        draw.ellipse([80, y, 98, y + 14], fill=(50, 255, 120), outline=(255, 255, 255), width=1)
        # ไฟบน Remote
        draw.ellipse([205, y, 223, y + 14], fill=(50, 255, 120), outline=(255, 255, 255), width=1)

    # ปุ่มสวิตช์ POWER
    draw.rectangle([105, 225, 145, 245], fill=(40, 40, 40))

    img.save(os.path.join(output_dir, "tester.png"))

    # -------------------------------------------------------------
    # 5. รูป Network Switch & Router (อุปกรณ์ต่อเครือข่าย)
    # -------------------------------------------------------------
    img, draw = create_base_canvas()
    # ตัวเครื่องสวิตช์สีฟ้า Sci-Fi
    draw.rectangle([40, 90, 260, 170], fill=(0, 100, 200), outline=(100, 220, 255), width=3)
    # พอร์ต LAN 1-8
    for i in range(8):
        x = 55 + (i * 24)
        draw.rectangle([x, 115, x + 16, 145], fill=(20, 30, 40), outline=(0, 255, 255), width=1)
        # ไฟ LED พอร์ต
        draw.ellipse([x + 4, 102, x + 12, 110], fill=(0, 255, 100))

    img.save(os.path.join(output_dir, "switch.png"))

    print("🎉 สร้างรูปภาพอุปกรณ์ Sci-Fi ครบถ้วนเรียบร้อยแล้ว ที่โฟลเดอร์ textures/items/")


if __name__ == "__main__":
    generate_all_equipment_textures()