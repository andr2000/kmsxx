from drm_atomic import DrmAtomic
import ctypes
import fcntl
import os
import pykms
import time

class Timer(object):
    timers = []

    def __init__(self, timeout, callback, data):
        self.timeout = time.clock_gettime(time.CLOCK_MONOTONIC) + timeout
        self.callback = callback
        self.data = data

        print("adding timer %f" % self.timeout)
        self.timers.append(self)
        self.timers.sort(key=lambda timer: timer.timeout)

    @classmethod
    def fire(_class):
        clk = time.clock_gettime(time.CLOCK_MONOTONIC)
        while len(_class.timers) > 0:
            timer = _class.timers[0]
            if timer.timeout > clk:
                break

            del _class.timers[0]
            print("fireing timer %f" % timer.timeout)
            timer.callback(timer.data)

    @classmethod
    def next_timeout(_class):
        clk = time.clock_gettime(time.CLOCK_MONOTONIC)
        if len(_class.timers) == 0 or _class.timers[0].timeout < clk:
            return None

        return _class.timers[0].timeout - clk


class Timeline(object):

    class sw_sync_create_fence_data(ctypes.Structure):
        _fields_ = [
            ('value', ctypes.c_uint32),
            ('name', ctypes.c_char * 32),
            ('fence', ctypes.c_int32),
        ]

    SW_SYNC_IOC_CREATE_FENCE = (3 << 30) | (ctypes.sizeof(sw_sync_create_fence_data) << 16) | (ord('W') << 8) | (0 << 0)
    SW_SYNC_IOC_INC = (1 << 30) | (ctypes.sizeof(ctypes.c_uint32) << 16) | (ord('W') << 8) | (1 << 0)

    class SWSync(object):
        def __init__(self, fd):
            self.fd = fd
        def __del__(self):
            os.close(self.fd)

    def __init__(self):
        self.value = 0
        try:
            self.fd = os.open('/sys/kernel/debug/sync/sw_sync', 0);
        except:
            raise RuntimeError('Failed to open sw_sync file')

    def close(self):
        os.close(self.fd)

    def create_fence(self, value):
        data = self.sw_sync_create_fence_data(value = value);
        ret = fcntl.ioctl(self.fd, self.SW_SYNC_IOC_CREATE_FENCE, data);
        if ret < 0:
            raise RuntimeError('Failed to create fence')

        return self.SWSync(data.fence)

    def signal(self, value):
        fcntl.ioctl(self.fd, self.SW_SYNC_IOC_INC, ctypes.c_uint32(value))
        self.value += value

class DrmAtomicFence(DrmAtomic):
    def __init__(self, cfg):
        super().__init__(cfg)
        self.timeline = Timeline()

    def init(self):
        self.setup_graphics()
        self.setup_selectors()
        self.set_mode()
        # do not do initial flip

    def run(self):
        timeout = Timer.next_timeout()
        print("--> timeout %s" % repr(timeout))
        events = self.sel.select(timeout)
        self.handle_events(events)
        Timer.fire()
        return True

    def handle_page_flip(self, frame, time):
        # Verify that the page flip hasn't completed before the timeline got
        # signaled.
        if self.timeline.value < 2 * self.flips - 1:
            raise RuntimeError('Page flip %u for fence %u complete before timeline (%u)!' %
                               (self.flips, 2 * self.flips - 1, self.timeline.value))
        super().handle_page_flip(frame, time)

    def flip(self, fb):
        # Flip the buffers with an in fence located in the future. The atomic
        # commit is asynchronous and returns immediately, but the flip should
        # not complete before the fence gets signaled.
        print("flipping with fence @%u, timeline is @%u" % (2 * self.flips - 1, self.timeline.value))
        fence = self.timeline.create_fence(2 * self.flips - 1)
        req = pykms.AtomicReq(self.drm.crtc.card)
        req.add(self.drm.crtc.primary_plane,
                { 'FB_ID': fb.id,
                  'IN_FENCE_FD': fence.fd })
        self.req_commit(req, False)
        del fence

        # Arm a timer to signal the fence in 0.5s.
        def timeline_signal(timeline):
            print("signaling timeline @%u" % timeline.value)
            timeline.signal(2)

        Timer(0.5, timeline_signal, self.timeline)

    def __del__(self):
        # Signal the timeline to complete all pending page flips
        self.timeline.signal(100)
