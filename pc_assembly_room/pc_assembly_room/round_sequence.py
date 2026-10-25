"""Room-local, in-memory sequence. Consecutive medium rounds never repeat."""
from dataclasses import dataclass
import random

@dataclass(frozen=True)
class BuildTarget:
    id: str
    motherboard: str
    cpu: str
    ram: str
    @property
    def required_parts(self):
        return {'motherboard':self.motherboard,'cpu':self.cpu,'ram':self.ram}

TARGETS = {
    'intel':BuildTarget('intel','mobo_lga','cpu_intel','ram_ddr4'),
    'amd':BuildTarget('amd','mobo_am5','cpu_amd','ram_ddr5'),
}

class RoundSequence:
    def __init__(self, first=None):
        if first is None:
            first = random.choice(tuple(TARGETS))
        if first not in TARGETS:raise ValueError('Unknown first build')
        self._next=first
    def next_target(self):
        target=TARGETS[self._next]
        self._next='amd' if target.id=='intel' else 'intel'
        return target
