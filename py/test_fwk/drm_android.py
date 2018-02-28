from drm_atomic import DrmAtomic
from drm_card import DrmCard
from framebuffers import FrameBuffers
from ion import Ion
import pykms

class DrmAndroid(DrmAtomic):
    def alloc_new_fb(self):
        if self.ion:
            return self.fb_allocator.create_fb_ion_raw(0)

        return self.fb_allocator.create_fb_self_import_raw(0)

    def setup_graphics(self):
        self.drm = DrmCard(self.cfg)
        # get the first vblank
        self.vblank_seq = self.wait_vblank(pykms.DRM_VBLANK_RELATIVE, 0)
        print('self.vblank_seq %d ' % self.vblank_seq)
        try:
            self.ion = Ion()
            print('Using %s ION heap' % self.cfg.ion_heap)
        except:
            print('WARNING! ION allocator is not available, using self import')
            self.ion = None

        self.fb_allocator = FrameBuffers(self.cfg, self.drm, self.ion, "XR24")
        self.front_buf, self.front_buf_origfb = self.alloc_new_fb()

    def wait_vblank(self, flags, sequence):
        return self.drm.crtc.wait_vblank(flags, sequence)

    def get_next_fb(self):
        return self.front_buf

    def draw_fb(self, fb):
        # do not draw now as base class wants
        pass

    def flip(self, fb):
        # do not flip as this is handled in complex on self.handle_page_flip
        pass

    def set_mode(self):
        self.drm.crtc.set_mode(self.drm.conn, self.front_buf, self.drm.mode)

    def handle_page_flip(self, frame, time):
        super().handle_page_flip(frame, time)
        # hold references to the fbs until we flip
        front_fb = self.front_buf
        front_buf_origfb = self.front_buf_origfb
        self.front_buf, self.front_buf_origfb = self.alloc_new_fb()
        super().draw_fb(self.front_buf)
        super().flip(self.front_buf)
        # delete external buffer first
        del front_fb
        # now delete dma-buf
        del front_buf_origfb
