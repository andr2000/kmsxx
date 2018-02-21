import pykms
import test_config

class DrmCard:
    def __init__(self, cfg):
        if cfg.with_omap:
            self.card = pykms.OmapCard()
        else:
            self.card = pykms.Card()

        self.res = pykms.ResourceManager(self.card)
        self.conn = self.res.reserve_connector(cfg.conn_name)
        self.crtc = self.res.reserve_crtc(self.conn)
        self.plane = self.res.reserve_generic_plane(self.crtc)
        self.mode = self.conn.get_default_mode()
        self.modeb = self.mode.to_blob(self.card)
