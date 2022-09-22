# !/usr/bin/python3
from libs.arp import ARPspoof
import optparse

parser = optparse.OptionParser()
parser.add_option('-t', '--target', dest = 'target_ip', help = 'IP address of the target computer')
parser.add_option('-r', '--router', dest = 'router_ip', help = 'IP address of the access point')
(options, _) = parser.parse_args()

required = ["target_ip", "router_ip"]
for r in required:
    if options.__dict__[r] is None:
        parser.error("parameter %s required"%r)




arp_spoofer = ARPspoof(options.target_ip, options.router_ip)
arp_spoofer.run()
