# lan_module.py
"""
LAN Room Module Integration Interface
ใช้สำหรับให้ Main Hub เรียกเปิด/ปิด ห้องปฏิบัติการสาย LAN
"""
from lan_logic import LANGameLogic
from lan_ui import LANGameUI

class LANRoomModule:
    def __init__(self, base_app):
        self.app = base_app
        self.logic = LANGameLogic()
        self.ui = None

    def load_module(self):
        """เรียกใช้เมื่อผู้เล่นเดินเข้าประตูห้อง LAN ในโปรแกรมหลัก"""
        if not self.ui:
            self.ui = LANGameUI(self.app, self.logic, self.app.timer)
        self.ui.show_difficulty_menu()

    def unload_module(self):
        """เรียกใช้เมื่อผู้เล่นออกจากห้อง LAN กลับไป Hub หลัก"""
        if self.ui:
            self.ui.hide_all()
            
    def get_results(self):
        """ส่งคืนผลลัพธ์คะแนนและดาวให้โปรแกรมหลักสะสม"""
        # คืนค่า เช่น {"stars": 3, "passed": True}
        return getattr(self, "last_result", {"stars": 0, "passed": False})