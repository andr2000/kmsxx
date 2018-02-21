from ion import Ion
import pykms
import test_config

class FrameBuffers:
    def create_fb_ion_raw(self, primary_plane):
        origfb = pykms.IonBuffer(self.ion.ion, Ion.ION_HEAPS[self.cfg.ion_heap],
                                 primary_plane, self.drm.mode.hdisplay,
                                 self.drm.mode.vdisplay, self.pixel_format);
        fb = pykms.ExtFramebuffer(self.drm.card, origfb.width, origfb.height,
                                  origfb.format, [origfb.prime_fd],
                                  [origfb.stride], [origfb.offset])
        # ION DMA buffer may come dirty, so reset it to all black
        if Ion.ION_HEAPS[self.cfg.ion_heap] == pykms.ION_HEAP_TYPE_DMA:
            pykms.draw_rect(fb, 0, 0, origfb.width, origfb.height,
                            pykms.RGB(0, 0, 0))
        return fb, origfb

    def create_fb_ion(self, primary_plane):
        fb, origfb = self.create_fb_ion_raw(primary_plane)
        self.origfbs.append(origfb)
        return fb

    def create_fb_self_import_raw(self, primary_plane):
        origfb = pykms.DumbFramebuffer(self.drm.card,
                                       self.drm.mode.hdisplay,
                                       self.drm.mode.vdisplay,
                                       self.pixel_format);
        fb = pykms.ExtFramebuffer(self.drm.card, origfb.width, origfb.height,
                                  origfb.format, [origfb.fd(primary_plane)],
                                  [origfb.stride(primary_plane)],
                                  [origfb.offset(primary_plane)])
        return fb, origfb

    def create_fb_self_import(self, primary_plane):
        fb, origfb = self.create_fb_self_import_raw(primary_plane)
        self.origfbs.append(origfb)
        return fb

    def create_fb_omap(self):
        return pykms.OmapFramebuffer(self.drm.card, self.drm.mode.hdisplay,
                                     self.drm.mode.vdisplay,
                                     self.pixel_format);

    def create_fb_drm(self):
        return pykms.DumbFramebuffer(self.drm.card, self.drm.mode.hdisplay,
                                     self.drm.mode.vdisplay,
                                     self.pixel_format);

    def create_fb(self):
        primary_plane = 0
        if self.cfg.with_ion:
            return self.create_fb_ion(primary_plane)

        if self.cfg.with_self_import:
            return self.create_fb_self_import(primary_plane)

        if self.cfg.with_omap:
            return self.create_fb_omap()

        return self.create_fb_drm()

    def create_fbs(self):
        fbs = []
        fbs.append(self.create_fb())
        fbs.append(self.create_fb())
        return fbs

    def __init__(self, cfg, drm, ion, pixel_format):
        self.cfg = cfg
        self.drm = drm
        self.ion = ion
        self.pixel_format = pixel_format
        # for ion/self-imported keep original framebuffers
        # until this object destroyed
        self.origfbs = []
