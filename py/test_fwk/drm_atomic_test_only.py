import sys

from drm_atomic import DrmAtomic

class DrmAtomicTestOnly(DrmAtomic):
    def handle_drm_event(self):
        for event in self.drm.card.read_events():
            print("Received %s event successfully (seq %d time %f)" %
                  (event.type, event.seq, event.time))

    def req_commit(self, req, modeset=True):
        ret = req.test(allow_modeset=modeset)
        if ret != 0:
            print('Atomic test failed: ' +str(ret))
            sys.exit(-1)
        req.commit(0, allow_modeset=modeset)

    def flip(self, fb):
        pass

    def run(self):
        super().run(1)
        return False
