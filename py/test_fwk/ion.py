import pykms

class Ion:
    ION_HEAPS = {
        "SYSTEM":           pykms.ION_HEAP_TYPE_SYSTEM,
        "SYSTEM_CONTIG":    pykms.ION_HEAP_TYPE_SYSTEM_CONTIG,
        "CARVEOUT":         pykms.ION_HEAP_TYPE_CARVEOUT,
        "CHUNK":            pykms.ION_HEAP_TYPE_CHUNK,
        "DMA":              pykms.ION_HEAP_TYPE_DMA,
    }

    def __init__(self):
        self.ion = pykms.Ion()
