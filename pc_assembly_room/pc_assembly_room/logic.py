"""ลอจิกการประกอบคอม — Python ล้วน ไม่ผูกกับ Panda3D (ทดสอบเดี่ยวได้)

ผลลัพธ์ทุกอย่างเป็นรหัส (Code) ไม่ใช่ข้อความ เพื่อให้เปลี่ยนภาษาได้
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional, Sequence


class Kind(Enum):
    MOTHERBOARD = "motherboard"
    CPU = "cpu"
    COOLER = "cooler"
    RAM = "ram"
    GPU = "gpu"
    STORAGE = "storage"
    PSU = "psu"


class Code(Enum):
    OK = "ok"
    UNKNOWN_PART = "unknown_part"
    UNKNOWN_SLOT = "unknown_slot"
    ALREADY_INSTALLED = "already_installed"  # ชิ้นส่วนนี้ติดตั้งอยู่แล้ว
    NOTHING_SELECTED = "nothing_selected"    # ยังไม่ได้เลือกชิ้นส่วน
    WRONG_SLOT = "wrong_slot"                # ประเภทไม่ตรงกับตำแหน่ง
    NEED_FIRST = "need_first"                # ต้องติดตั้งตำแหน่งอื่นก่อน
    SLOT_FILLED = "slot_filled"              # ตำแหน่งนี้มีของแล้ว
    WRONG_BUILD = "wrong_build"
    INCOMPATIBLE = "incompatible"            # สเปกเข้ากันไม่ได้
    EMPTY_SLOT = "empty_slot"                # ตำแหน่งว่าง (ถอดไม่ได้)
    HAS_DEPENDENTS = "has_dependents"        # มีชิ้นส่วนอื่นติดตั้งทับอยู่


# รหัสที่นับเป็น "ข้อผิดพลาด" ของผู้เล่น (ส่งต่อให้ระบบกลางนับดาว/ข้อผิดพลาด)
MISTAKE_CODES = frozenset({Code.WRONG_SLOT, Code.NEED_FIRST, Code.INCOMPATIBLE, Code.WRONG_BUILD})


@dataclass(frozen=True, eq=False)
class Part:
    id: str
    kind: Kind
    specs: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Slot:
    id: str
    kind: Kind
    requires: tuple = ()  # id ของ slot ที่ต้องติดตั้งก่อน


@dataclass(frozen=True)
class Rule:
    """part ใน slot ต้องมีค่า spec ตรงกับ part ใน other"""
    slot: str
    other: str
    spec: str


@dataclass(frozen=True)
class Result:
    code: Code
    part: str = ""  # id ชิ้นส่วนที่เกี่ยวข้อง
    slot: str = ""  # id ตำแหน่งที่ใช้ประกอบข้อความ (ดูหมายเหตุใน place/remove)

    @property
    def ok(self) -> bool:
        return self.code is Code.OK


@dataclass(frozen=True)
class CheckResult:
    complete: bool
    missing: tuple = ()    # slot ที่ยังว่าง
    conflicts: tuple = ()  # slot ที่สเปกขัดกัน


class AssemblyState:
    def __init__(self, parts: Sequence[Part], slots: Sequence[Slot], rules: Sequence[Rule] = (), required_parts: Optional[Mapping[str, str]] = None):
        self._parts = {p.id: p for p in parts}
        self._slots = {s.id: s for s in slots}
        if len(self._parts) != len(parts) or len(self._slots) != len(slots):
            raise ValueError("id ของ part/slot ซ้ำกัน")
        for s in slots:
            for r in s.requires:
                if r not in self._slots:
                    raise ValueError(f"slot '{s.id}' requires '{r}' ซึ่งไม่มีอยู่")
        for r in rules:
            if r.slot not in self._slots or r.other not in self._slots:
                raise ValueError(f"rule อ้างถึง slot ที่ไม่มีอยู่: {r}")
        self._required_parts = dict(required_parts or {})
        for sid,pid in self._required_parts.items():
            if sid not in self._slots or pid not in self._parts or self._slots[sid].kind is not self._parts[pid].kind:
                raise ValueError('Invalid required part for slot: '+sid)
        self._rules = tuple(rules)
        self.reset()

    # ---------- สถานะ ----------
    def reset(self) -> None:
        self._installed: dict = {}  # slot_id -> part_id
        self._selected: Optional[str] = None
        self._mistakes = 0

    @property
    def selected(self) -> Optional[str]:
        return self._selected

    @property
    def mistakes(self) -> int:
        return self._mistakes

    @property
    def installed(self) -> dict:
        return dict(self._installed)

    def part_in(self, slot_id: str) -> Optional[str]:
        return self._installed.get(slot_id)

    def slot_of(self, part_id: str) -> Optional[str]:
        for s, p in self._installed.items():
            if p == part_id:
                return s
        return None

    # ---------- การกระทำ ----------
    def select(self, part_id: str) -> Result:
        if part_id not in self._parts:
            return Result(Code.UNKNOWN_PART, part=part_id)
        if self.slot_of(part_id) is not None:
            return Result(Code.ALREADY_INSTALLED, part=part_id)
        self._selected = part_id
        return Result(Code.OK, part=part_id)

    def deselect(self) -> None:
        self._selected = None

    def preview_place(self, slot_id: str) -> Result:
        """Evaluate a target without changing selection, installation or mistakes."""
        from copy import copy
        preview = copy(self)
        preview._installed = dict(self._installed)
        return preview.place(slot_id)

    def place(self, slot_id: str) -> Result:
        """วางชิ้นส่วนที่เลือกไว้ลงตำแหน่ง
        slot ใน Result: WRONG_SLOT/SLOT_FILLED = ตำแหน่งที่คลิก,
        NEED_FIRST = ตำแหน่งที่ต้องติดตั้งก่อน, INCOMPATIBLE = ตำแหน่งที่สเปกขัดกัน
        """
        if self._selected is None:
            return Result(Code.NOTHING_SELECTED)
        slot = self._slots.get(slot_id)
        if slot is None:
            return Result(Code.UNKNOWN_SLOT, slot=slot_id)
        part = self._parts[self._selected]
        if slot_id in self._installed:
            return Result(Code.SLOT_FILLED, part=part.id, slot=slot_id)
        if part.kind is not slot.kind:
            return self._mistake(Result(Code.WRONG_SLOT, part=part.id, slot=slot_id))
        for req in slot.requires:
            if req not in self._installed:
                return self._mistake(Result(Code.NEED_FIRST, part=part.id, slot=req))
        conflict = self._find_conflict(slot_id, part)
        if conflict:
            return self._mistake(Result(Code.INCOMPATIBLE, part=part.id, slot=conflict))
        if slot_id in self._required_parts and part.id != self._required_parts[slot_id]:
            return self._mistake(Result(Code.WRONG_BUILD, part=part.id, slot=slot_id))
        self._installed[slot_id] = part.id
        self._selected = None
        return Result(Code.OK, part=part.id, slot=slot_id)

    def remove(self, slot_id: str) -> Result:
        """ถอดชิ้นส่วนออก; HAS_DEPENDENTS: slot ใน Result = ตำแหน่งที่ต้องถอดก่อน"""
        if slot_id not in self._slots:
            return Result(Code.UNKNOWN_SLOT, slot=slot_id)
        if slot_id not in self._installed:
            return Result(Code.EMPTY_SLOT, slot=slot_id)
        for s in self._slots.values():
            if slot_id in s.requires and s.id in self._installed:
                return Result(Code.HAS_DEPENDENTS, part=self._installed[slot_id], slot=s.id)
        part_id = self._installed.pop(slot_id)
        return Result(Code.OK, part=part_id, slot=slot_id)

    def check(self) -> CheckResult:
        missing = tuple(s for s in self._slots if s not in self._installed)
        conflicts = tuple(
            s for s, p in self._installed.items()
            if self._find_conflict(s, self._parts[p], ignore_self=True)
        )
        return CheckResult(not missing and not conflicts, missing, conflicts)

    # ---------- ภายใน ----------
    def _mistake(self, result: Result) -> Result:
        if result.code in MISTAKE_CODES:
            self._mistakes += 1
        return result

    def _find_conflict(self, slot_id: str, part: Part, ignore_self: bool = False) -> Optional[str]:
        for r in self._rules:
            if r.slot == slot_id:
                other_slot, other_spec = r.other, self._installed.get(r.other)
            elif r.other == slot_id:
                other_slot, other_spec = r.slot, self._installed.get(r.slot)
            else:
                continue
            if other_spec is None:
                continue
            if ignore_self and other_slot == slot_id:
                continue
            if self._parts[other_spec].specs.get(r.spec) != part.specs.get(r.spec):
                return other_slot
        return None
