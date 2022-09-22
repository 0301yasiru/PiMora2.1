# !/usr/bin/python3
from libs.arp import ARPdetect
import optparse

parser = optparse.OptionParser()
parser.add_option('-i', '--interface', dest = 'interface', help = 'The interface for the network connection')
(options, _) = parser.parse_args()

required = ["interface"]
for r in required:
    if options.__dict__[r] is None:
        parser.error("parameter %s required"%r)


arp_detector = ARPdetect(options.interface)
arp_detector.detect()