from drm_base import DrmBase
import pykms

class DrmAtomic(DrmBase):
    def __init__(self, cfg):
        super().__init__(cfg)

    def req_commit(self, req, modeset=True):
        req.commit(allow_modeset=modeset)

    def set_mode(self):
        self.drm.card.disable_planes()

        req = pykms.AtomicReq(self.drm.card)
        req.add(self.drm.conn, "CRTC_ID", self.drm.crtc.id)
        req.add(self.drm.crtc, {"ACTIVE": 1,
                        "MODE_ID": self.drm.modeb.id})
        fb = self.get_next_fb()
        req.add(self.drm.plane, {"FB_ID": fb.id,
                        "CRTC_ID": self.drm.crtc.id,
                        "SRC_X": 0 << 16,
                        "SRC_Y": 0 << 16,
                        "SRC_W": self.drm.mode.hdisplay << 16,
                        "SRC_H": self.drm.mode.vdisplay << 16,
                        "CRTC_X": 0,
                        "CRTC_Y": 0,
                        "CRTC_W": self.drm.mode.hdisplay,
                        "CRTC_H": self.drm.mode.vdisplay})
        print('set_mode FB_ID %d' % fb.id)
        self.req_commit(req)

    def flip(self, fb):
        req = pykms.AtomicReq(self.drm.card)
        req.add(self.drm.crtc.primary_plane, "FB_ID", fb.id)
        self.req_commit(req)
