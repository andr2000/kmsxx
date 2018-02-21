import selectors
import pykms
import sys

from drm_card import DrmCard
from framebuffers import FrameBuffers
from ion import Ion

class DrmBase():
    EVENT_DRM = 'drm'
    EVENT_KEY = 'key'

    def __init__(self, cfg):
        super().__init__()

        self.cfg = cfg
        self.bar_width = 20
        self.bar_speed = 8
        self.bar_xpos = 0
        self.front_buf = 0
        self.flips = 0
        self.frames = 0
        self.time = 0
        self.flips_last = 0
        self.frame_last = 0
        self.time_last = 0

    ############################################################################
    # Generic test setup
    ############################################################################
    def init(self):
        self.setup_graphics()
        self.setup_selectors()
        self.set_mode()
        self.handle_page_flip(0, 0)

    def setup_selectors(self):
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.drm.card.fd, selectors.EVENT_READ, self.EVENT_DRM)
        self.sel.register(sys.stdin, selectors.EVENT_READ, self.EVENT_KEY)

    def handle_key_event(self):
        sys.stdin.readline()
        sys.exit(0)

    def handle_events(self, events):
        for key, mask in events:
            if (key.data == self.EVENT_DRM):
                self.handle_drm_event()
            else:
                self.handle_key_event()

    ############################################################################
    # Run one iteration of the test
    ############################################################################
    def run(self, timeout=None):
        events = self.sel.select(timeout)
        if not events:
            print('Error: timeout receiving event')
        else:
            self.handle_events(events)
        return True

    ############################################################################
    # DRM handling
    ############################################################################
    def setup_graphics(self):
        self.drm = DrmCard(self.cfg)
        if self.cfg.with_ion:
            self.ion = Ion()
        else:
            self.ion = None
        self.fb_allocator = FrameBuffers(self.cfg, self.drm, self.ion, "XR24")
        self.fbs = self.fb_allocator.create_fbs()

    def get_next_fb(self):
        if self.front_buf == 0:
            fb = self.fbs[1]
        else:
            fb = self.fbs[0]

        self.front_buf = self.front_buf ^ 1
        return fb

    def wait_vblank(self):
        if self.cfg.wait_vblank:
            ret = self.drm.crtc.wait_vblank(pykms.DRM_VBLANK_RELATIVE, 1)
            if ret != 0:
                print('Wait for Vblank failed: ' + str(ret))
                return ret

        return 0

    def handle_drm_event(self):
        for ev in self.drm.card.read_events():
            if ev.type == pykms.DrmEventType.FLIP_COMPLETE:
                self.handle_page_flip(ev.seq, ev.time)

    def flip(self, fb):
        if self.wait_vblank() == 0:
            self.drm.crtc.page_flip(fb)

    def set_mode(self):
        self.drm.crtc.set_mode(self.drm.conn, self.get_next_fb(), self.drm.mode)

    def draw_fb(self, fb):
        current_xpos = self.bar_xpos;
        old_xpos = (current_xpos + (fb.width - self.bar_width - self.bar_speed)) % (fb.width - self.bar_width);
        new_xpos = (current_xpos + self.bar_speed) % (fb.width - self.bar_width);
        self.bar_xpos = new_xpos
        pykms.draw_color_bar(fb, old_xpos, new_xpos, self.bar_width)

    def handle_page_flip(self, frame, time):
        self.flips += 1

        if self.time_last == 0:
            self.frame_last = frame
            self.time_last = time

        # Print statistics every 5 seconds.
        time_delta = time - self.time_last
        if time_delta >= 5:
            frame_delta = frame - self.frame_last
            flips_delta = self.flips - self.flips_last
            print("Frame rate: %f (%u/%u frames in %f s)" %
                  (frame_delta / time_delta, flips_delta, frame_delta, time_delta))

            self.frame_last = frame
            self.flips_last = self.flips
            self.time_last = time

        fb = self.get_next_fb()
        self.draw_fb(fb)
        self.flip(fb)
