# lan_logic.py

COLOR_HEX_MAP = {
    "White-Orange": (0.9, 0.5, 0.2, 1),
    "Orange": (0.9, 0.3, 0.0, 1),
    "White-Green": (0.3, 0.8, 0.3, 1),
    "Blue": (0.1, 0.3, 0.9, 1),
    "White-Blue": (0.4, 0.6, 0.9, 1),
    "Green": (0.0, 0.7, 0.1, 1),
    "White-Brown": (0.6, 0.4, 0.2, 1),
    "Brown": (0.4, 0.2, 0.1, 1),
}

# มาตรฐาน T568B
T568B_CORRECT = [
    "White-Orange", "Orange", "White-Green", "Blue",
    "White-Blue", "Green", "White-Brown", "Brown"
]
T568B_CORRECT_ORDER = T568B_CORRECT

# มาตรฐาน T568A
T568A_CORRECT = [
    "White-Green", "Green", "White-Orange", "Blue",
    "White-Blue", "Orange", "White-Brown", "Brown"
]
T568A_CORRECT_ORDER = T568A_CORRECT

# ข้อมูลอุปกรณ์สำหรับแสดงบน Info Card (สถานีที่ 2)
EQUIPMENT_INFO = {
    "สาย UTP": {"desc": "สายสัญญาณ UTP สำหรับส่งข้อมูลผ่านระบบ Ethernet Network", "icon": "utp"},
    "หัว RJ45": {"desc": "หัวคอนเนกเตอร์สำหรับเข้าปลายสาย LAN เพื่อเสียบเข้าพอร์ต", "icon": "rj45"},
    "คีมย้ำ RJ45": {"desc": "คีมย้ำหัว RJ45 ใช้สำหรับการตัด ปอก และย้ำหัวสาย LAN", "icon": "crimper"},
    "Cable Tester": {"desc": "เครื่องวัดสายสัญญาณ LAN ใช้วัดการส่งสัญญาณไฟฟ้า Pin 1-8", "icon": "tester"}
}

STATION_TITLES = {
    1: "เริ่มภารกิจ LAN Networking",
    2: "เลือกอุปกรณ์ (UTP, RJ45, คีมย้ำ, Tester)",
    3: "เตรียมสาย (ปอกเปลือก & คลายเกลียว)",
    4: "เรียงสีสาย LAN",
    5: "ตัดและเข้าหัว RJ45",
    6: "ทดสอบสายสัญญาณ (Cable Test)",
    7: "ต่อสายเข้าเครือข่าย (PC -> Switch -> Router)",
    8: "ตรวจสอบ Network Status (Link / IP / Ping)",
    9: "สรุปคะแนนภารกิจ"
}


class LANGameLogic:
    def __init__(self):
        self.difficulty = "easy"
        self.max_time = 120
        self.hints_enabled = True
        self.allow_request_hint = False
        self.target_standard = "T568B"
        
        self.current_station = 1
        self.completed_stations = set()
        self.unlocked_station = 1
        self.current_pins = [None] * 8
        self.errors_count = 0

    def set_difficulty(self, level):
        self.difficulty = level
        self.current_station = 1
        self.completed_stations.clear()
        self.unlocked_station = 1
        self.reset_pins()
        self.errors_count = 0
        
        if level == "easy":
            self.max_time = 120
            self.hints_enabled = True
            self.allow_request_hint = True
            self.target_standard = "T568B"
        elif level == "medium":
            self.max_time = 90
            self.hints_enabled = False
            self.allow_request_hint = True
            self.target_standard = "T568A"
        elif level == "hard":
            self.max_time = 60
            self.hints_enabled = False
            self.allow_request_hint = False
            self.target_standard = "T568A"

    def reset_pins(self):
        self.current_pins = [None] * 8

    def can_access_station(self, station_num):
        return station_num <= self.unlocked_station

    def complete_station(self, station_num):
        self.completed_stations.add(station_num)
        if station_num == self.unlocked_station and station_num < 9:
            self.unlocked_station += 1

    def check_pin_correctness(self):
        target_list = T568A_CORRECT if self.target_standard == "T568A" else T568B_CORRECT
        return self.current_pins == target_list

    def get_current_hint(self):
        if not self.hints_enabled and not self.allow_request_hint:
            return "ระดับยาก: ไม่มีคำใบ้ช่วยเหลือ!"

        hints_map = {
            1: "เดินไปที่ป้าย START ด้านหน้าเพื่อเริ่มภารกิจ",
            2: "หยิบอุปกรณ์ให้ครบ 4 ชนิด: สาย UTP, หัว RJ45, คีมย้ำ และ Cable Tester",
            3: "กดปุ่มปอกเปลือกสาย จากนั้นคลายเกลียวสายออกทั้ง 4 คู่",
            4: f"เรียงสี {self.target_standard}: " + (
                "ขาวเขียว -> เขียว -> ขาวส้ม -> น้ำเงิน -> ขาวน้ำเงิน -> ส้ม -> ขาวน้ำตาล -> น้ำตาล" 
                if self.target_standard == "T568A" else 
                "ขาวส้ม -> ส้ม -> ขาวเขียว -> น้ำเงิน -> ขาวน้ำเงิน -> เขียว -> ขาวน้ำตาล -> น้ำตาล"
            ),
            5: "ใช้คีมตัดปลายสายให้เสมอ แล้วเสียบเข้าหัว RJ45 ก่อนกดกดย้ำหัว",
            6: "เสียบสายทั้งสองฝั่งเข้า Cable Tester แล้วกดทดสอบสัญญาณ",
            7: "เชื่อมต่อสาย LAN จาก PC ไป Switch และต่อจาก Switch ไป Router",
            8: "ตรวจสอบไฟ Link Active -> ตั้งค่า IP 192.168.1.100 -> ทดสอบ Ping Pass",
            9: "ภารกิจเสร็จสมบูรณ์! รับผลสรุปคะแนนดาว"
        }
        return hints_map.get(self.current_station, "")

    def advance_station(self):
        if self.current_station < 9:
            self.current_station += 1
            return True
        return False

    def set_pin(self, index, color_name):
        if 0 <= index < 8:
            self.current_pins[index] = color_name

    def evaluate(self, time_left):
        return self.evaluate_final_score(time_left)

    def evaluate_final_score(self, time_left):
        if time_left <= 0:
            return {"success": False, "stars": 0, "message": "❌ หมดเวลา! ไม่สามารถทำภารกิจได้ทัน"}

        color_correct = self.check_pin_correctness()
        if not color_correct:
            self.errors_count += 1

        time_used = self.max_time - time_left
        
        if color_correct and self.errors_count == 0 and time_used <= (self.max_time * 0.6):
            stars = 3
            rank = "ยอดเยี่ยม (Perfect!)"
        elif color_correct and self.errors_count <= 1:
            stars = 2
            rank = "ดี (Good Job!)"
        else:
            stars = 1
            rank = "ผ่านเกณฑ์ (Practice Needed)"

        return {
            "success": True,
            "stars": stars,
            "message": f"🎉 ผ่านภารกิจสำเร็จ!\nมาตรฐานที่ใช้: {self.target_standard}\nเวลาที่ใช้: {int(time_used)} วินาที\nระดับประเมิน: {rank}"
        }