# PC Assembly Room — Module Contract (ร่าง)

> API ส่วน "โปรแกรมหลักเรียกห้อง" เป็นร่างชั่วคราว รอผู้ดูแลสถาปัตยกรรมประกาศรูปแบบจริง

| หัวข้อ (หมวด 6) | รายละเอียด |
|---|---|
| ชื่อห้อง / เจ้าของ | PC Assembly / (ใส่ชื่อผู้รับผิดชอบ) |
| หน้าที่ | มินิเกมเลือกและประกอบชิ้นส่วนคอมพิวเตอร์ ตรวจความเข้ากันได้ |
| โปรแกรมหลักเรียก | `room = PCAssemblyRoom(base, translator, font_path, pointer, on_complete)` แล้ว `room.enter(parent_nodepath)` |
| ส่งข้อมูลเข้า | `translator` (ภาษา), `font_path` (ฟอนต์ไทย), `pointer` (อินพุต) |
| ส่งผลลัพธ์กลับ | `on_complete({"mistakes": n})` เรียกครั้งเดียวเมื่อตรวจถูกต้อง; อ่าน `room.mistakes` ได้ตลอด |
| ออกจากห้อง | `room.exit()` |
| คืนทรัพยากร | `exit()` ลบ node ฉาก, collision, UI ข้อความ และยกเลิก event ทั้งหมด |
| เริ่มรอบใหม่ | `room.reset()` |
| Dependencies | Python, Panda3D เท่านั้น (ไม่เพิ่มแพ็กเกจอื่น) |
| วิธีทดสอบ | ลอจิก: `python -m unittest pc_assembly_room.tests.test_logic` (ไม่ต้องมี Panda3D) / ฉาก: `python -m pc_assembly_room.run_standalone --font <ฟอนต์ไทย>` |
| ไฟล์ที่แก้ได้ | ทุกไฟล์ในโฟลเดอร์ `pc_assembly_room/` |
| ไฟล์ส่วนกลางที่ห้ามแก้ | ระบบภาษา ระบบควบคุม/กล้อง ระบบเปลี่ยนห้อง ระบบคะแนน entry point ของโปรแกรมหลัก |

## โครงสร้าง
- `logic.py` ลอจิกล้วน (ไม่พึ่ง Panda3D) · `data.py` ชิ้นส่วน/ตำแหน่ง/กฎ · `strings.py` ข้อความ ไทย/อังกฤษ
- `scene.py` ฉาก 3D จากทรงกล่อง + การคลิกเลือก · `room.py` จุดเชื่อม · `pointer.py` ชั้นแยกอินพุต
- `run_standalone.py` ตัวทดสอบเดี่ยว (ไม่ใช่ entry point หลัก)

## Scene update: iteration 1
Central desk, six category displays, motherboard pedestal, grey/white lab and blue trim.
Procedural low-poly assets; not a photoreal reproduction of the reference.

Run from the parent folder:
python -m pc_assembly_room.run_walkthrough --lang th --font "C:/Windows/Fonts/tahoma.ttf" --difficulty easy

Difficulty: easy / medium / hard. Easy has motherboard and PSU preinstalled,
five remaining tasks and a compatible set. Medium shows empty slots. Hard hides
slot highlights. Both medium and hard offer compatibility choices.
Timer stops on successful checking; R resets. No star thresholds are invented.
Callback adds elapsed_seconds and difficulty; the team API is still a draft.
Pending: Hub integration, shared scoring and graphical difficulty menu.
Windows input and Thai rendering require target-machine verification.
