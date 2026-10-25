"""ข้อมูลชิ้นส่วน/ตำแหน่ง/กฎความเข้ากันได้ (เนื้อหาตัวอย่าง — เจ้าของเนื้อหาควรตรวจทาน)"""
from .logic import Kind, Part, Rule, Slot

PARTS = (
    Part("mobo_lga", Kind.MOTHERBOARD, {"socket": "LGA1700", "ram_type": "DDR4"}),
    Part("mobo_am5", Kind.MOTHERBOARD, {"socket": "AM5", "ram_type": "DDR5"}),
    Part("cpu_intel", Kind.CPU, {"socket": "LGA1700"}),
    Part("cpu_amd", Kind.CPU, {"socket": "AM5"}),
    Part("cooler_std", Kind.COOLER),
    Part("ram_ddr4", Kind.RAM, {"ram_type": "DDR4"}),
    Part("ram_ddr5", Kind.RAM, {"ram_type": "DDR5"}),
    Part("gpu_std", Kind.GPU),
    Part("ssd_std", Kind.STORAGE),
    Part("psu_std", Kind.PSU),
)

SLOTS = (
    Slot("psu", Kind.PSU),
    Slot("motherboard", Kind.MOTHERBOARD),
    Slot("storage", Kind.STORAGE, ("motherboard",)),
    Slot("cpu", Kind.CPU, ("motherboard",)),
    Slot("cooler", Kind.COOLER, ("cpu",)),
    Slot("ram", Kind.RAM, ("motherboard",)),
    Slot("gpu", Kind.GPU, ("motherboard",)),
)

RULES = (
    Rule("cpu", "motherboard", "socket"),
    Rule("ram", "motherboard", "ram_type"),
)
