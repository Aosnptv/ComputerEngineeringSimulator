# Main Hub Visual Design Gate

สถานะ: **รออนุมัติก่อน implementation**  
ขอบเขต: ปรับภาพ Main Hub เท่านั้น ไม่เปลี่ยน PC Assembly, lifecycle, input หรือ minigame logic

## 1. Floor plan (เมตร)

พื้นที่ภายในคงกรอบเดิมประมาณ 20 × 20 เมตร เพดานสูง 6 เมตร และแกนเดินกลางกว้าง 5.5 เมตร

```text
ทิศเหนือ / ผนังกระจกและอาคาร CPE ภายนอก
┌──────────────────────────────────────────┐
│  KS-5       สวน/ทางเดินภายนอก      KS-6 │
│                                          │
│  KS-3       Console กลาง           KS-4 │
│             (minigame access)            │
│                                          │
│  KS-1        Guide Robot            KS-2 │
│                                          │
│      จุดเกิดผู้เล่น + ป้ายควบคุม         │
└──────────────────────────────────────────┘
ทิศใต้ / ทางเข้า
```

- Knowledge Station ทั้ง 6 จุดอยู่สองข้างทางหลัก ระยะเดินถึงจุดโต้ตอบไม่เกิน 2.3 เมตร
- Console กลางเป็น landmark หลักและไม่บัง sightline ไปยังผนังกระจก
- ทางเดินหลักไม่มี prop ยื่นเข้าพื้นที่เคลื่อนที่ และคง camera height 2.2 เมตร
- ภายนอกกระจกแบ่งเป็นอาคารเรียน, ทางเดิน campus, แนวต้นไม้ และเสาไฟแบบ low-poly

## 2. Visual palette

| บทบาท | สีหลัก | การใช้งาน |
|---|---|---|
| Deep navy | `#07162B`–`#102B49` | ผนัง, plinth, panel background |
| Structural blue | `#1C5275` | กรอบ, โครงสร้าง, workstation |
| Cyan signal | `#16C7E6` | navigation cue, active state, edge light |
| Cool white | `#E8F7FF` | ตัวอักษรและพื้นผิวที่ต้องอ่านง่าย |
| Station accent | สีเดิมของแต่ละ station | แยกหัวข้อโดยไม่เปลี่ยน identity |
| Exterior neutral | `#334D63`, `#6E8492`, เขียวหม่น | อาคาร/ทางเดิน/ต้นไม้ภายนอก |

## 3. Lighting และ material guide

- ใช้ shared ambient + directional key/fill เดิมเป็นฐาน เพื่อไม่สร้าง native render state ซ้ำ
- เพิ่มเฉพาะ fill light ที่ reuse ได้และมีจำนวนคงที่; ไม่สร้าง light ใหม่ทุกครั้งที่เข้า Hub
- วัสดุใช้ conventional Panda3D materials: matte powder coat, brushed metal, frosted glass และ emissive-look ด้วย `setLightOff` เฉพาะ accent
- หลีกเลี่ยง per-object shader และ transparency ซ้อนหลายชั้นบน Intel UHD 630
- ข้อความ world-space ต้องมี contrast อย่างน้อย 4.5:1 และมีระยะอ่านเป้าหมาย 2–6 เมตร

## 4. Asset / prop inventory

- workstation 6 ชุด: โต๊ะ, monitor, keyboard silhouette, cable channel, station beacon
- central console: plinth, display, status bars, room-selection marker
- engineering props: rack cabinet, PCB display, network patch panel, oscilloscope silhouette, tool trolley
- architecture: mullion, ceiling grid, wall rail, column, skirting, door frame
- exterior: อาคาร CPE แบบ 2–3 mass, หน้าต่างแบบ instanced, walkway, curb, tree 3 แบบ, bench และเสาไฟ
- signage: station number, bilingual title, interaction cue, minigame availability state

ทั้งหมดใช้ primitive/instanced low-poly geometry หรือ asset ที่มี license/provenance ชัดเจนเท่านั้น

## 5. File change list ที่เสนอ

- `ComputerEngineeringVR/src/rooms/main_hub.py` — layout, reusable prop builders, lighting/material application
- `ComputerEngineeringVR/src/content.py` — bilingual labels/copy เท่านั้น หากจำเป็น
- `ComputerEngineeringVR/src/rooms/adapters/hub_adapter.py` — เฉพาะ lifecycle hooks หากต้อง preload shared immutable assets
- `tests/test_main_hub_visual_contract.py` — station count, landmarks, bounds, shared-resource contract
- `reports/beta_readiness/` — screenshots และ performance evidence ก่อน/หลัง

จะไม่แก้ `pc_assembly_room`, `MainVrGameCPE-main` หรือสร้าง `ShowBase` เพิ่ม

## 6. Performance budget

- 30 FPS ขั้นต่ำ, เป้าหมาย 60 FPS ที่ 1280×720 บน Intel UHD 630 หรือ exhibition hardware จริง
- Hub render descendants เป้าหมาย ≤ 500
- dynamic lights ที่มีผลต่อ geometry ≤ 4 และต้อง reuse ข้าม lifecycle
- transparent surfaces ≤ 12 ชิ้น, หลีกเลี่ยง overdraw เต็มจอ
- texture memory เพิ่มจาก baseline ≤ 32 MB; texture สูงสุดทั่วไป 1024²
- Hub↔room 30 รอบ: handles หลัง warm-up ไม่โตเกิน 5 ต่อรอบโดยเฉลี่ย, prepared resources ไม่โตต่อเนื่อง
- private memory หลัง warm-up 5 รอบถึงรอบ 30 โตไม่เกิน 10 MB

## 7. Visual acceptance criteria

1. ผู้ทดสอบระบุ console และ Knowledge Station ทั้ง 6 ได้จากจุดเกิดโดยไม่เปิดเมนู
2. UI ไทย/อังกฤษไม่ล้น panel ที่ 1280×720 และ 1920×1080
3. ทางเดินและจุดโต้ตอบไม่ถูก prop ใหม่บัง
4. exterior อ่านเป็น campus engineering building ไม่ใช่ผนังสีเรียบ
5. station active/nearby state แยกได้ด้วยทั้งสีและรูปทรง/ความสว่าง
6. ไม่มีความเปลี่ยนแปลงต่อภาพหรือ gameplay ของ PC Assembly
7. screenshot review ผ่านมุม spawn, center console, station pair ทั้งสาม และ exterior
8. ผ่าน performance budget และ 30-transition soak test บน target hardware

## Approval gate

ต้องอนุมัติ floor plan, palette, prop scope และ performance budget นี้ก่อนเริ่มเปลี่ยน visual architecture ของ Main Hub
