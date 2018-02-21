from drm_atomic import DrmAtomic
from drm_atomic_fence import DrmAtomicFence
from drm_atomic_sync import DrmAtomicSync
from drm_atomic_test_only import DrmAtomicTestOnly
from drm_base import DrmBase

class TestFactory:
    def __init__(self, cfg):
        self.cfg = cfg

    def __enter__(self):
        if self.cfg.force_legacy:
            self.handler = DrmBase(self.cfg)
        elif self.cfg.atomic_fence:
            self.handler = DrmAtomicFence(self.cfg)
        elif self.cfg.atomic_test:
            self.handler = DrmAtomicTestOnly(self.cfg)
        elif self.cfg.atomic_sync:
            self.handler = DrmAtomicSync(self.cfg)
        else:
            self.handler = DrmAtomic(self.cfg)
        return self.handler

    def __exit__(self, type, value, traceback):
        del self.handler

