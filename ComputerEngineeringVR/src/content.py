from typing import TypedDict


class Station(TypedDict):
    id: str
    en: tuple[str, str]
    th: tuple[str, str]
    pos: tuple[float, float]
    color: tuple[float, float, float, float]


def station_text(station: Station, language: str) -> tuple[str, str]:
    return station["th"] if language == "th" else station["en"]


STATIONS: list[Station] = [
    {
        "id": "hardware",
        "en": ("Hardware", "Explore CPU, RAM, storage, and how a computer is assembled."),
        "th": ("ฮาร์ดแวร์", "เรียนรู้ CPU, RAM, อุปกรณ์จัดเก็บข้อมูล และการประกอบคอมพิวเตอร์"),
        "pos": (-5.7, -1),
        "color": (0.13, 0.73, 0.95, 1),
    },
    {
        "id": "programming",
        "en": ("Programming", "Use algorithms, variables, and conditions to solve problems."),
        "th": ("การเขียนโปรแกรม", "ใช้ขั้นตอนวิธี ตัวแปร และเงื่อนไขเพื่อแก้ปัญหา"),
        "pos": (-5.7, 3),
        "color": (0.48, 0.72, 1, 1),
    },
    {
        "id": "network",
        "en": ("Networks", "See how devices communicate through LANs, IPs, and routers."),
        "th": ("เครือข่าย", "ดูการสื่อสารของอุปกรณ์ผ่าน LAN, IP และเราเตอร์"),
        "pos": (-5.7, 7),
        "color": (0.38, 0.85, 0.65, 1),
    },
    {
        "id": "database",
        "en": ("Databases", "Organize, search, and protect structured information."),
        "th": ("ฐานข้อมูล", "จัดระเบียบ ค้นหา และดูแลข้อมูลอย่างเป็นระบบ"),
        "pos": (5.7, -1),
        "color": (1, 0.74, 0.36, 1),
    },
    {
        "id": "cybersecurity",
        "en": ("Cybersecurity", "Protect systems and information from digital threats."),
        "th": ("ความปลอดภัยไซเบอร์", "ปกป้องระบบและข้อมูลจากภัยคุกคามทางดิจิทัล"),
        "pos": (5.7, 3),
        "color": (1, 0.48, 0.63, 1),
    },
    {
        "id": "ai",
        "en": ("Artificial Intelligence", "Discover how machines recognize patterns and make predictions."),
        "th": ("ปัญญาประดิษฐ์", "ค้นพบวิธีที่เครื่องจักรเรียนรู้รูปแบบและคาดการณ์"),
        "pos": (5.7, 7),
        "color": (0.73, 0.59, 1, 1),
    },
]

TEXT = {
    "en": {
        "title": "COMPUTER ENGINEERING LAB",
        "welcome": "Click the computer in the middle to choose rooms 1–3.",
        "stations": "KNOWLEDGE STATIONS",
        "help": "W A S D  Move    Right-drag  Look    E  Explore",
        "near": "Press E: {name}",
        "robot": "Press E to talk to your guide",
        "robot_message": "Welcome! Choose a station to explore computer engineering.",
        "computer_near": "Click the computer or press E: rooms 1–3",
    },
    "th": {
        "title": "ห้องเรียนวิศวกรรมคอมพิวเตอร์",
        "welcome": "คลิกจอคอมกลางห้องเพื่อเลือกห้อง 1–3",
        "stations": "สถานีความรู้",
        "help": "W A S D  เดิน    คลิกขวาค้างแล้วลาก  หัน    E  สำรวจ",
        "near": "กด E: {name}",
        "robot": "กด E เพื่อคุยกับหุ่นยนต์ไกด์",
        "robot_message": "ยินดีต้อนรับ! เลือกสถานีเพื่อเรียนรู้วิศวกรรมคอมพิวเตอร์",
        "computer_near": "คลิกจอคอมหรือกด E: เลือกห้อง 1–3",
    },
}
