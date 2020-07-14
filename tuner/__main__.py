
import argparse
import pyaudio

# import tuner


def main(argv=None):
    # Collect all input device ids
    p = pyaudio.PyAudio()
    is_input = lambda id : p.get_device_info_by_host_api_device_index(0, id).get('maxInputChannels') > 0
    all_devs = range (0, p.get_host_api_info_by_index(0).get('deviceCount'))
    in_devs = list(filter(is_input, all_devs))

    # Parse args
    parser = argparse.ArgumentParser(prog='tuner')
    parser.add_argument('-ld', '--listdevices', help='List input devices', action='store_true')
    parser.add_argument('-d', '--device', help='Input device id', type=int, choices=in_devs)
    args = parser.parse_args(argv)

    # List input devices
    if args.listdevices:
        print('id   name')
        for id in in_devs:
            info = p.get_device_info_by_host_api_device_index(0, id)
            print(f'{id}    {info.get("name")}')

    else:
        import tuner # TODO: implement
  

if __name__ == '__main__':
    main()