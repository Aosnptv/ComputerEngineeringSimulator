"""Pure, read-only hint planning for the next unfinished assembly step."""
from copy import copy
from .data import SLOTS
STEP_ORDER = ('motherboard', 'cpu', 'ram', 'storage', 'cooler', 'gpu', 'psu')

def next_hint(state, parts):
    """Return (slot, compatible available part ids), without changing the round."""
    sid = next((sid for sid in STEP_ORDER if state.part_in(sid) is None), None)
    if sid is None:
        return None, ()
    kind = next(s.kind for s in SLOTS if s.id == sid)
    candidates = []
    for part in parts:
        if part.kind != kind or state.slot_of(part.id) is not None:
            continue
        preview = copy(state)
        preview._installed = dict(state.installed)
        preview.select(part.id)
        if preview.preview_place(sid).ok:
            candidates.append(part.id)
    return sid, tuple(candidates)

def preview_part(state, part_id, parts):
    """Evaluate an unheld display part, without selecting it in the live state."""
    part = next(p for p in parts if p.id == part_id)
    sid = next(s.id for s in SLOTS if s.kind == part.kind)
    preview = copy(state)
    preview._installed = dict(state.installed)
    preview.select(part_id)
    return preview.preview_place(sid)
