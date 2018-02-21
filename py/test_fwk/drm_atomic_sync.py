import time

from drm_atomic import DrmAtomic

class DrmAtomicSync(DrmAtomic):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.frame = 1

    def req_commit(self, req, modeset=True):
        req.commit_sync(allow_modeset=modeset)

    def handle_drm_event(self):
        pass

    def run(self):
        # do not block, we'll block on DRM sync commit instead
        events = self.sel.select(-1)
        if not events:
            self.handle_page_flip(self.frame, time.time())
            self.frame += 1
        self.handle_events(events)
        return True
