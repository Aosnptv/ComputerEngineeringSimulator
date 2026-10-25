"""ข้อความทั้งหมดของห้อง (ไทย/อังกฤษ) — แยกออกจากลอจิก

translator = ฟังก์ชัน t(key, **kwargs) -> str
ถ้าโปรแกรมหลักมีระบบภาษากลาง ให้ส่ง translator ของระบบกลางเข้ามาแทน (รอผู้ดูแลกำหนด API)
"""
TEXT = {
    "th": {
        "ui.title": "ห้องประกอบคอมพิวเตอร์",
        "ui.hint": "คลิกชิ้นส่วนทางขวา แล้วคลิกตำแหน่งบนเคส (คลิกชิ้นส่วนที่ติดตั้งแล้วเพื่อถอดออก)",
        "ui.check": "ตรวจคำตอบ",
        "ui.mistakes": "ข้อผิดพลาด: {n}",
        "msg.ok_select": "เลือก: {part}",
        "msg.ok_place": "ติดตั้ง {part} แล้ว",
        "msg.ok_remove": "ถอด {part} ออกแล้ว",
        "msg.deselected": "ยกเลิกการเลือกแล้ว",
        "msg.unknown_part": "ไม่พบชิ้นส่วนนี้",
        "msg.unknown_slot": "ไม่พบตำแหน่งนี้",
        "msg.already_installed": "ชิ้นส่วนนี้ติดตั้งอยู่แล้ว",
        "msg.nothing_selected": "ยังไม่ได้เลือกชิ้นส่วน",
        "msg.wrong_slot": "{part} ไม่ใช่ชิ้นส่วนสำหรับตำแหน่ง {slot}",
        "msg.need_first": "ต้องติดตั้ง {slot} ก่อน",
        "msg.slot_filled": "ตำแหน่ง {slot} มีชิ้นส่วนติดตั้งอยู่แล้ว",
        "msg.incompatible": "{part} ใช้ร่วมกับ {slot} ที่ติดตั้งอยู่ไม่ได้",
        "msg.empty_slot": "ตำแหน่ง {slot} ยังว่างอยู่",
        "msg.has_dependents": "ต้องถอด {slot} ออกก่อน",
        "msg.check_complete": "ประกอบครบและถูกต้อง!",
        "msg.check_incomplete": "ยังประกอบไม่ครบ: เหลืออีก {n} ตำแหน่ง",
        "part.mobo_lga": "เมนบอร์ด Intel (LGA1700, DDR4)",
        "part.mobo_am5": "เมนบอร์ด AMD (AM5, DDR5)",
        "part.cpu_intel": "CPU Intel (LGA1700)",
        "part.cpu_amd": "CPU AMD (AM5)",
        "part.cooler_std": "ชุดระบายความร้อน CPU",
        "part.ram_ddr4": "RAM DDR4",
        "part.ram_ddr5": "RAM DDR5",
        "part.gpu_std": "การ์ดจอ",
        "part.ssd_std": "SSD",
        "part.psu_std": "พาวเวอร์ซัพพลาย",
        "slot.psu": "พาวเวอร์ซัพพลาย",
        "slot.motherboard": "เมนบอร์ด",
        "slot.storage": "ที่เก็บข้อมูล (SSD)",
        "slot.cpu": "CPU",
        "slot.cooler": "ชุดระบายความร้อน",
        "slot.ram": "RAM",
        "slot.gpu": "การ์ดจอ",
    },
    "en": {
        "ui.title": "PC Assembly Room",
        "ui.hint": "Click a part on the right, then click a spot on the case (click an installed part to remove it)",
        "ui.check": "Check",
        "ui.mistakes": "Mistakes: {n}",
        "msg.ok_select": "Selected: {part}",
        "msg.ok_place": "Installed {part}",
        "msg.ok_remove": "Removed {part}",
        "msg.deselected": "Selection cleared",
        "msg.unknown_part": "Part not found",
        "msg.unknown_slot": "Slot not found",
        "msg.already_installed": "This part is already installed",
        "msg.nothing_selected": "No part selected yet",
        "msg.wrong_slot": "{part} does not belong in the {slot} position",
        "msg.need_first": "Install the {slot} first",
        "msg.slot_filled": "The {slot} position is already filled",
        "msg.incompatible": "{part} is not compatible with the installed {slot}",
        "msg.empty_slot": "The {slot} position is empty",
        "msg.has_dependents": "Remove the {slot} first",
        "msg.check_complete": "Everything is installed correctly!",
        "msg.check_incomplete": "Not finished: {n} position(s) left",
        "part.mobo_lga": "Intel motherboard (LGA1700, DDR4)",
        "part.mobo_am5": "AMD motherboard (AM5, DDR5)",
        "part.cpu_intel": "Intel CPU (LGA1700)",
        "part.cpu_amd": "AMD CPU (AM5)",
        "part.cooler_std": "CPU cooler",
        "part.ram_ddr4": "DDR4 RAM",
        "part.ram_ddr5": "DDR5 RAM",
        "part.gpu_std": "Graphics card",
        "part.ssd_std": "SSD",
        "part.psu_std": "Power supply",
        "slot.psu": "power supply",
        "slot.motherboard": "motherboard",
        "slot.storage": "storage (SSD)",
        "slot.cpu": "CPU",
        "slot.cooler": "CPU cooler",
        "slot.ram": "RAM",
        "slot.gpu": "graphics card",
    },
}

EXTRA = {
    "en": {
        "ui.hint_walk": "WASD: walk | Mouse: look | Left click: pick/place | Right click: return | R: restart | Esc: exit test",
        "ui.hover_place": "Install: {slot}", "msg.hands_full": "Return or install the held part first.",
        "msg.returned": "Part returned to its display.", "msg.preinstalled": "This part is already fitted for the easy level.",
        "ui.progress": "{level} | Installed {n}/7", "ui.next": "Next: {slot}",
        "ui.time": "Time {minutes:02d}:{seconds:02d}",
        "level.easy": "Easy", "level.medium": "Medium", "level.hard": "Hard",
        "lab.components": "COMPUTER COMPONENTS", "lab.guide": "PC ASSEMBLY LAB",
        "lab.cpu": "CPU", "lab.ram": "RAM", "lab.ssd": "SSD", "lab.gpu": "GPU",
        "lab.psu": "POWER SUPPLY", "lab.cooler": "CPU COOLER",
    },
    "th": {
        "ui.hint_walk": "WASD เดิน | เมาส์มอง | คลิกซ้ายหยิบ/วาง | คลิกขวาคืน | R เริ่มใหม่ | Esc ออกจากตัวทดสอบ",
        "ui.hover_place": "ติดตั้ง: {slot}", "msg.hands_full": "ติดตั้งหรือคืนชิ้นส่วนที่ถือก่อน",
        "msg.returned": "คืนชิ้นส่วนไปยังชั้นแล้ว", "msg.preinstalled": "ชิ้นส่วนนี้ติดตั้งให้แล้วในระดับง่าย",
        "ui.progress": "{level} | ติดตั้งแล้ว {n}/7", "ui.next": "ขั้นถัดไป: {slot}",
        "ui.time": "เวลา {minutes:02d}:{seconds:02d}",
        "level.easy": "ง่าย", "level.medium": "ปานกลาง", "level.hard": "ยาก",
        "lab.components": "ส่วนประกอบคอมพิวเตอร์", "lab.guide": "ห้องปฏิบัติการประกอบคอมพิวเตอร์",
        "lab.cpu": "CPU", "lab.ram": "RAM", "lab.ssd": "SSD", "lab.gpu": "การ์ดจอ",
        "lab.psu": "พาวเวอร์ซัพพลาย", "lab.cooler": "ชุดระบายความร้อน CPU",
    },
}
for _lang, _strings in EXTRA.items():
    TEXT[_lang].update(_strings)

PLAY_TEXT = {'en': {'lab.name': 'NOVA  |  PC ASSEMBLY LAB',
        'lab.motherboard': 'MOTHERBOARD',
        'lab.monitor': 'ASSEMBLY GUIDE\n'
                       '1. Select a part\n'
                       '2. Match its socket\n'
                       '3. Install all parts\n'
                       '4. Press CHECK',
        'lab.components': 'COMPUTER COMPONENTS\nCPU  /  RAM  /  SSD\nMATCH SOCKET + MEMORY TYPE',
        'lab.guide': 'INSTALLATION GUIDE\nCPU > RAM > SSD > COOLER > GPU\nCHECK BEFORE POWER ON',
        'play.goal': 'Install all 7 components, then press the green CHECK button.',
        'play.held': 'HOLDING: {part} | Right click: return to display',
        'play.empty_hands': 'EMPTY HANDS | Find parts on the labelled display stands.',
        'play.press_check': 'All fitted: press CHECK',
        'play.aim': 'Aim at the matching labelled pad on the desk or at the socket inside the case.',
        'play.pick_hint': 'Walk to a display. Aim at a part or its plinth and left click.',
        'play.click_pick': 'Left click: pick up',
        'play.click_remove': 'Left click: remove',
        'play.valid': 'CORRECT: left click to install',
        'play.click': 'Left click',
        'play.finished': 'Assembly complete! R: new round | Esc: exit test',
        'play.move_closer': 'Move closer and aim at a part, installation pad or CHECK button.',
        'play.carry_easy': 'Follow the GREEN pad / socket. RED means wrong type, incompatible or blocked.',
        'play.carry': 'Match the held part to a labelled installation pad or case socket.',
        'short.psu': 'PSU',
        'short.motherboard': 'BOARD',
        'short.storage': 'SSD',
        'short.cpu': 'CPU',
        'short.cooler': 'COOLER',
        'short.ram': 'RAM',
        'short.gpu': 'GPU'},
 'th': {'lab.name': 'NOVA | ห้องประกอบคอมพิวเตอร์',
        'lab.motherboard': 'เมนบอร์ด',
        'lab.monitor': 'คู่มือประกอบ\n1. เลือกอุปกรณ์\n2. ตรวจตำแหน่ง\n3. ติดตั้งให้ครบ\n4. กดตรวจคำตอบ',
        'lab.components': 'ส่วนประกอบคอมพิวเตอร์\nCPU / RAM / SSD\nตรวจซ็อกเก็ตและชนิดหน่วยความจำ',
        'lab.guide': 'คำแนะนำการติดตั้ง\nCPU > RAM > SSD > ชุดระบายความร้อน > GPU\nตรวจสอบก่อนเปิดเครื่อง',
        'play.goal': 'ติดตั้งอุปกรณ์ให้ครบ 7 ประเภท แล้วกดปุ่มตรวจคำตอบสีเขียว',
        'play.held': 'กำลังถือ: {part} | คลิกขวาเพื่อคืนชั้น',
        'play.empty_hands': 'มือว่าง | เลือกอุปกรณ์จากแท่นจัดแสดงตามหมวดหมู่',
        'play.press_check': 'ติดตั้งครบแล้ว: กดตรวจคำตอบ',
        'play.aim': 'เล็งแผ่นชื่อชิ้นส่วนบนโต๊ะ หรือตำแหน่งภายในเคส แล้วคลิกซ้าย',
        'play.pick_hint': 'เดินเข้าใกล้ชั้น เล็งอุปกรณ์หรือแท่น แล้วคลิกซ้ายเพื่อหยิบ',
        'play.click_pick': 'คลิกซ้ายเพื่อหยิบ',
        'play.click_remove': 'คลิกซ้ายเพื่อถอด',
        'play.valid': 'ถูกต้อง: คลิกซ้ายเพื่อติดตั้ง',
        'play.click': 'คลิกซ้าย',
        'play.finished': 'ประกอบสำเร็จ! R เริ่มรอบใหม่ | Esc ออกจากตัวทดสอบ',
        'play.move_closer': 'เดินเข้าใกล้แล้วเล็งอุปกรณ์ แผ่นติดตั้ง หรือปุ่มตรวจคำตอบ',
        'play.carry_easy': 'ตามแผ่นหรือช่องสีเขียว | สีแดงคือผิดประเภท สเปกไม่ตรง หรือยังติดตั้งไม่ได้',
        'play.carry': 'เล็งแผ่นชื่ออุปกรณ์บนโต๊ะ หรือตำแหน่งที่ตรงกันในเคส',
        'short.psu': 'PSU',
        'short.motherboard': 'BOARD',
        'short.storage': 'SSD',
        'short.cpu': 'CPU',
        'short.cooler': 'COOLER',
        'short.ram': 'RAM',
        'short.gpu': 'GPU'}}
for _lang, _strings in PLAY_TEXT.items():
    TEXT[_lang].update(_strings)

for _lang in ('th', 'en'):
    TEXT[_lang]['play.arrow'] = 'v'

RESULT_TEXT = {'en': {'play.counter': 'Installed {n}/7',
        'play.ready_check': '7/7 COMPLETE - click the GREEN CHECK button in front of the monitor.',
        'result.title': 'ASSEMBLY COMPLETE!',
        'result.message': 'Great work! Your computer is correctly assembled.',
        'result.time': 'Time used: {time}',
        'result.errors': 'Mistakes: {n}',
        'result.replay': 'Play again',
        'result.menu': 'Main menu',
        'result.draft': 'Trial star criteria - pending team agreement',
        'menu.title': 'PC ASSEMBLY ROOM',
        'menu.subtitle': 'Choose a difficulty | No time limit',
        'menu.note': 'Standalone room menu. Team Main Hub integration is pending.',
        'menu.quit': 'Exit',
        'menu.back_hub': 'Back to Main Hub',
        'result.policy': '3 stars: <= {t3} and <= {e3} mistakes\n'
                         '2 stars: <= {t2} and <= {e2} mistakes\n'
                         'Otherwise: 1 star on completion'},
 'th': {'play.counter': 'ติดตั้งแล้ว {n}/7',
        'play.ready_check': 'ครบ 7/7 แล้ว - กดปุ่มตรวจคำตอบสีเขียวด้านหน้าจอคอม',
        'result.title': 'ประกอบสำเร็จ!',
        'result.message': 'เยี่ยมมาก! คุณประกอบคอมพิวเตอร์ได้ถูกต้องแล้ว',
        'result.time': 'เวลาที่ใช้: {time}',
        'result.errors': 'ข้อผิดพลาด: {n} ครั้ง',
        'result.replay': 'เล่นซ้ำ',
        'result.menu': 'กลับเมนูหลัก',
        'result.draft': 'เกณฑ์ดาวทดลอง - รอทีมตกลงเกณฑ์จริง',
        'menu.title': 'ห้องประกอบคอมพิวเตอร์',
        'menu.subtitle': 'เลือกระดับความยาก | เล่นได้ไม่จำกัดเวลา',
        'menu.note': 'เมนูตัวทดสอบห้อง ยังไม่ได้เชื่อม Main Hub ของทีม',
        'menu.quit': 'ออกจากโปรแกรม',
        'menu.back_hub': 'กลับห้องหลัก',
        'result.policy': '3 ดาว: เวลาไม่เกิน {t3} และผิดไม่เกิน {e3} ครั้ง\n'
                         '2 ดาว: เวลาไม่เกิน {t2} และผิดไม่เกิน {e2} ครั้ง\n'
                         'กรณีอื่น: 1 ดาวเมื่อเล่นสำเร็จ'}}
for _lang, _strings in RESULT_TEXT.items():
    TEXT[_lang].update(_strings)

HINT_TEXT = {'en': {'hint.button': 'HINT [H]',
        'hint.help': 'Need help? Press H or click the BLUE HINT button. Hints do not reduce stars.',
        'hint.steps': 'Steps: BOARD > CPU > RAM > SSD > COOLER > GPU > PSU',
        'hint.detail': 'STEP: {slot}\n'
                       'Choose: {part}\n'
                       'Pick it from its display, then click the GREEN pad / socket. Right click '
                       'to return a wrong part.',
        'hint.unavailable': 'Check prerequisites for {slot}. Remove incompatible parts, then ask '
                            'for a hint again.'},
 'th': {'hint.button': 'ดูคำใบ้ [H]',
        'hint.help': 'ต้องการความช่วยเหลือ กด H หรือคลิกปุ่มคำใบ้สีน้ำเงิน | ขอคำใบ้ไม่หักดาว',
        'hint.steps': 'ขั้นตอน: BOARD > CPU > RAM > SSD > COOLER > GPU > PSU',
        'hint.detail': 'ขั้นตอน: {slot}\n'
                       'เลือก: {part}\n'
                       'หยิบจากแท่น แล้วคลิกแผ่นหรือช่องสีเขียว หากถือผิดชิ้นให้คลิกขวาคืนก่อน',
        'hint.unavailable': 'ตรวจอุปกรณ์ที่ต้องติดตั้งก่อน {slot} '
                            'ถอดชิ้นที่ไม่เข้ากันแล้วขอคำใบ้อีกครั้ง'}}
for _lang, _strings in HINT_TEXT.items():
    TEXT[_lang].update(_strings)

AUTO_HINT_TEXT = {'en': {'hint.help': 'Follow the next step above. Green display = recommended part. Right click = '
                     'return.',
        'auto.compatible': 'Compatible - you can use this part',
        'auto.no_board': 'Not selected yet - choose a motherboard first',
        'auto.detail': 'BOARD: {board}\nNEXT: {slot}\nRECOMMENDED: {part}',
        'auto.install_now': 'Compatible part: click the GREEN labelled pad or socket to install.',
        'auto.return_part': 'Right click to return it, then choose the recommended part.'},
 'th': {'hint.help': 'ทำตามขั้นตอนด้านบน | แท่นสีเขียวคืออุปกรณ์แนะนำ | คลิกขวาคืนชิ้นส่วน',
        'auto.compatible': 'เข้ากันได้ สามารถใช้อุปกรณ์นี้ได้',
        'auto.no_board': 'ยังไม่ได้เลือก ให้เลือกเมนบอร์ดก่อน',
        'auto.detail': 'เมนบอร์ด: {board}\nขั้นตอนถัดไป: {slot}\nอุปกรณ์แนะนำ: {part}',
        'auto.install_now': 'อุปกรณ์เข้ากันได้ คลิกแผ่นชื่อหรือช่องสีเขียวเพื่อติดตั้ง',
        'auto.return_part': 'คลิกขวาคืน แล้วเลือกอุปกรณ์ที่แนะนำ'}}
for _lang, _strings in AUTO_HINT_TEXT.items():
    TEXT[_lang].update(_strings)
    TEXT[_lang].pop("hint.button", None)

PHYSICAL_ROOM_TEXT = {'en': {'auto.detail': 'NEXT: {slot} | Choose: {part}\n'
                       'Board: {board} | Match the part to its coloured frame inside the case.',
        'auto.install_now': 'Click the green frame INSIDE THE CASE to install.',
        'medium.aim': 'Aim at the matching frame INSIDE THE CASE, then left click.',
        'play.carry': 'Match the part shape and size to the frame INSIDE THE CASE. Left click to '
                      'install.',
        'lab.components': 'COMPUTER COMPONENTS',
        'lab.guide': 'GPU / COMPONENT INSTALLATION GUIDE'},
 'th': {'auto.detail': 'ขั้นตอน: {slot} | เลือก: {part}\n'
                       'เมนบอร์ด: {board} | เทียบรูปทรงและขนาดกับกรอบสีในเคส',
        'auto.install_now': 'คลิกกรอบสีเขียวภายในเคสเพื่อติดตั้ง',
        'medium.aim': 'เล็งกรอบตำแหน่งภายในเคส แล้วคลิกซ้ายเพื่อติดตั้ง',
        'play.carry': 'เทียบรูปทรงและขนาดกับกรอบภายในเคส แล้วคลิกซ้ายเพื่อติดตั้ง',
        'lab.components': 'ส่วนประกอบคอมพิวเตอร์',
        'lab.guide': 'คำแนะนำการติดตั้งอุปกรณ์'}}
for _lang, _strings in PHYSICAL_ROOM_TEXT.items():
    TEXT[_lang].update(_strings)

ROUND_TEXT = {'en': {'round.target': 'Target: {build}',
        'round.intel': 'Intel / LGA1700 / DDR4',
        'round.amd': 'AMD / AM5 / DDR5',
        'msg.wrong_build': '{part} does not match this round. Choose {expected}.'},
 'th': {'round.target': 'โจทย์: {build}',
        'round.intel': 'Intel / LGA1700 / DDR4',
        'round.amd': 'AMD / AM5 / DDR5',
        'msg.wrong_build': '{part} ไม่ตรงโจทย์รอบนี้ ให้เลือก {expected}'}}
for _lang, _strings in ROUND_TEXT.items():
    TEXT[_lang].update(_strings)

missing_keys: list = []  # รายงานข้อความที่ยังไม่มีคำแปล


def make_translator(lang: str = "th"):
    def t(key: str, **kwargs) -> str:
        text = TEXT.get(lang, {}).get(key)
        if text is None:
            if (lang, key) not in missing_keys:
                missing_keys.append((lang, key))
            text = TEXT["en"].get(key, key)
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return t
