import argparse
from ion import Ion

class TestConfig():
    def parse_test_args(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('--connector',
                            dest='conn_name', required=False, default="",
                            help="Use connector name provided")

        group_ioctl = parser.add_mutually_exclusive_group()
        group_ioctl.add_argument('--force-legacy', action='store_true',
                                 dest='force_legacy', required=False,
                                 help='Force legacy mode for atomic drivers: use\
                                       MODE_SETCRTC + MODE_PAGE_FLIP')
        group_ioctl.add_argument('--atomic-test', action='store_true',
                                 dest='atomic_test', required=False,
                                 help='Use DRM_MODE_ATOMIC_TEST_ONLY')
        group_ioctl.add_argument('--atomic-sync', action='store_true',
                                 dest='atomic_sync', required=False,
                                 help='Use synchronous (blocking) atomic operations')
        group_ioctl.add_argument('--atomic-fence', action='store_true',
                                 dest='atomic_fence', required=False,
                                 help='Use fences to synchronize page flips')

        group_alloc = parser.add_mutually_exclusive_group()
        group_alloc.add_argument('--self-import', action='store_true',
                                 dest='with_self_import', required=False,
                                 help='Self import dma-buf while allocating dumb buffers')
        group_alloc.add_argument('--omap', action='store_true',
                                 dest='with_omap', required=False,
                                 help='Use OMAP extensions to allocate dumb buffers')
        group_alloc.add_argument('--ion', action='store_true',
                                 dest='with_ion', required=False,
                                 help='Use ION to allocate dumb buffers')

        parser.add_argument('--ion-heap', default="SYSTEM", choices=Ion.ION_HEAPS,
                            dest='ion_heap', required=False,
                            help='Use ION heap: ' + ' | '.join(Ion.ION_HEAPS.keys()))

        parser.add_argument('--vblank', default=False, action='store_true',
                            dest='wait_vblank', required=False,
                            help='Wait for vblank before page flipping')

        parser.parse_args(namespace=self)

    def print_test_title(self):
        if self.force_legacy:
            print('Test legacy mode: use SETCRTC + PAGE_FLIP')
        elif self.atomic_test:
            print('\tTest DRM_MODE_ATOMIC_TEST_ONLY')
        elif self.atomic_sync:
            print('Test synchronous (blocking) atomic operations')
        elif self.atomic_fence:
            print('Test fences to synchronize page flips')
        else:
            print('Test atomic page flips')

        if self.wait_vblank:
            print('\tWait for vblank before page flipping')

        if self.with_ion:
            print('\tUse ION for buffer allocation')
        elif self.with_omap:
            print('\tUse OMAP extensions for buffer allocation')
        elif self.with_self_import:
            print('\tUse self imported PRIME for buffer allocation')
        else:
            print('\tUse DRM dumb')

    def __init__(self):
        self.parse_test_args()
        self.print_test_title()
