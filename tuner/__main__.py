#!/usr/bin/python

# Standard library imports
import argparse
import signal
import sys

# Third party imports
import pyaudio

# Local application imports
from tuner import Tuner


def main(argv=None):
    # Bind signal handler
    signal.signal(signal.SIGINT, signal_handler)

    # Collect all input device ids
    p = pyaudio.PyAudio()
    is_input = lambda id : p.get_device_info_by_host_api_device_index(0, id).get('maxInputChannels') > 0
    all_devs = range (0, p.get_host_api_info_by_index(0).get('deviceCount'))
    in_devs = list(filter(is_input, all_devs))

    # Parse args
    parser = argparse.ArgumentParser(prog='tuner')
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
    parser.add_argument('-l', '--listdevices', help='List input devices', action='store_true')
    parser.add_argument('-d', '--device', help='Input device id', type=int, choices=in_devs)
    args = parser.parse_args(argv)

    # List input devices
    if args.listdevices:
        print('id    name')
        for id in in_devs:
            info = p.get_device_info_by_host_api_device_index(0, id)
            print(f' {id}    {info.get("name")}')

    # Run tuner
    else:
        t = Tuner(args.device)
        t.go(args.verbose)


def signal_handler(sig, frame):
    # TODO: cleanup
    sys.exit(0)
  

if __name__ == '__main__':
    main()