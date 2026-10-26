# Manual QA Checklist — Beta Gate

บันทึกชื่อผู้ทดสอบ, วันที่, Python/Panda3D, GPU/driver, resolution และ commit/working-tree fingerprint ก่อนเริ่ม ห้ามใช้การเรียก method ภายในเพื่อข้าม picking หรือ completion logic

## Desktop startup และ Main Hub

1. รัน `python -B ComputerEngineeringVR/src/main.py` โดยไม่เปิด SteamVR
2. รอ intro จบและทดสอบปุ่ม Skip ในรอบแยก
3. เลือกภาษาไทย; ตรวจข้อความไม่ล้น จากนั้น New Session และทำซ้ำภาษาอังกฤษ
4. เดิน WASD, หมุนด้วยลูกศร, เปิด/ปิด mouse-look ด้วยปุ่มขวา
5. เดินถึง Knowledge Station ทั้ง 6 และกด `E`; บันทึกว่าชื่อ/คำอธิบายตรงหัวข้อ
6. คลิก console กลาง; ยืนยัน PC Assembly ใช้งานจริง และ LAN/Programming ระบุเป็น placeholder ตามสภาพจริง

## PC Assembly Easy — full playthrough

1. เลือก Easy; ยืนยันของติดตั้งเริ่มต้น 2/7, elapsed timer เดินต่อเนื่องและไม่มี time limit
2. ใช้ WASD และ mouse aim หยิบชิ้นส่วนจริงจากโต๊ะ
3. วางผิด slot อย่างน้อยหนึ่งครั้ง; ยืนยัน feedback และ mistake count เพิ่มหนึ่งครั้งเท่านั้น
4. วางถูกครบทุกชิ้นตามลำดับ dependency
5. กด CHECK ผ่าน interaction จริง; ยืนยัน result, เวลา, mistakes และดาว 1–3 ดวง
6. กด Replay; ยืนยัน state/timer/mistakes reset และเล่นได้อีก
7. กด `R` ระหว่างเกม; ยืนยัน reset โดยไม่เพิ่ม task/event ซ้ำ
8. กด `Tab`, Resume, `Tab`, Back to Main Hub; ยืนยัน cursor/camera คืนค่า
9. เข้าใหม่แล้วกด `Esc`; ต้องกลับ Hub เพียงครั้งเดียวและไม่ปิดแอป

## PC Assembly Medium — full playthrough

1. เลือก Medium; ยืนยันไม่มี preinstalled parts และ target/spec ของรอบปรากฏ
2. ทดสอบ wrong type, incompatible CPU/RAM และ blocked dependency อย่างละหนึ่งครั้ง
3. ประกอบ build ที่ valid ผ่าน picking/placement จริงจนครบ และตรวจ result/stars
4. Replay สองครั้ง; target รอบถัดไปต้องไม่ซ้ำติดกัน
5. กลับเมนู PC แล้วกลับ Hub; ตรวจ cursor/camera/task stability

## Session และ localization

1. ทำผลสำเร็จหนึ่งรอบแล้วกด New Session ที่ Hub
2. ยืนยันผล/selected difficulty ถูกล้าง แต่ภาษาปัจจุบันยังอยู่
3. ทำ flow สำคัญทั้งไทยและอังกฤษ: Hub → PC menu → gameplay → result → Hub

## Soak/performance บน exhibition hardware

1. เปิด Task Manager/เครื่องมือวัดที่ได้รับอนุมัติ
2. ทำ Hub↔PC gameplay 30 รอบ โดยเริ่ม gameplay จริงทุกครั้ง
3. บันทึก private bytes, working set, handles, FPS และ GPU renderer ที่รอบ 0/1/2/5/10/20/30
4. หลัง warm-up รอบ 5: handles ต้องไม่โตต่อเนื่อง, prepared resources คงที่, private memory รอบ 5→30 ≤ 10 MB
5. FPS ต้องไม่ต่ำกว่า 30 ระหว่าง gameplay; เป้าหมาย 60

## VR hardware gate (ต้องมี package/runtime/HMD ที่อนุมัติ)

1. ยืนยัน active OpenXR runtime และรุ่น SteamVR
2. ต่อ HMD/controller และตรวจ runtime เห็นอุปกรณ์
3. ติดตั้ง dependency ใน environment แยกหลังอนุมัติ exact versions เท่านั้น
4. ทดสอบ stereo swapchain, head pose, left/right controller pose/select, recenter, focus loss และถอด HMD
5. ปิด runtime แล้วรัน desktop ปกติ; desktop ต้องยังเปิดได้

## Hard difficulty — design approval required

ก่อน implement ต้องอนุมัติอย่างน้อย: รายการ task/parts, preinstalled state, compatibility constraints, hint policy, mistake semantics, completion rule และเกณฑ์เวลา/ความผิดสำหรับ 1–3 ดาว ห้ามนำ label `Hard` ที่มีอยู่ใน strings มาเท่ากับ gameplay ที่พร้อมแล้ว
