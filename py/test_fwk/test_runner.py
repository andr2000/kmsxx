#!/usr/bin/env python3

from test_config import TestConfig
from test_factory import TestFactory

def main():
    try:
        with TestFactory(TestConfig()) as test:
            test.init()
            while test.run():
                continue
    finally:
        print("Done")

if __name__ == '__main__':
    main()