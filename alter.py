#
# #!/usr/bin/env python2
# -*- coding:utf8 -*-
# ----------------
# forked from dnspod official client
# modified by Justin Wong <bigeagle(at)xdlinux.info>
# License: MIT
# ----------------

import http.client, urllib.request, urllib.parse, urllib.error
import socket
import argparse
import time
# import fcntl
import struct
from xml.etree import ElementTree
from getpass import getpass

# DOMAIN=snomiao.com
# EMAIL=snomiao@gmail.com
# INTERVAL=5
# LOGIN_TOKEN=59179,9cad176bf676e06b1ef41a5e45f443c7
# SUB_DOMAIN=xiaoling

DEBUG = False
params = dict(
    login_email="snomiao@gmail.com", # replace with your email
    login_password="", # replace with your password
    format="json",
    domain_id=None, # replace with your domain_od, can get it by API Domain.List
    record_id=None, # replace with your record_id, can get it by API Record.List
    sub_domain="", # replace with your sub_domain
    record_line="默认",
    record_type="A"
)

def ddns(ip):
    params.update(dict(value=ip))
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Record.Modify", urllib.parse.urlencode(params), headers)
    
    response = conn.getresponse()
    if DEBUG: print(( response.status, response.reason))
    data = response.read()
    if DEBUG: print( data)
    conn.close()
    return response.status == 200

def get_domain_id(domain_name):
    keys = ["login_email", "login_password"]
    _param = { k:v for k,v in params.items() if k in keys }

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Domain.list", urllib.parse.urlencode(_param), headers)
    response = conn.getresponse()
    id = None
    etree = ElementTree.parse(response)
    for domain in  etree.findall("domains/item"):
        if domain.find("name").text == domain_name:
            id = domain.find("id").text          
    conn.close()
    if id:
        return id
    else:
        raise Exception("Record '"+domain_name+"' not found!")

def get_record_id():
    keys = ["login_email", "login_password", "domain_id"]
    _param = { k:v for k,v in params.items() if k in keys }
    subdomain = params["sub_domain"]
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Record.List", urllib.parse.urlencode(_param), headers)
    response = conn.getresponse()
    etree = ElementTree.parse(response)
    id = None
    for record in  etree.findall("records/item"):
        if record.find("name").text == subdomain:
            if DEBUG: print(( "Found", record.find("name").text))
            if id:
                raise Exception("Multipule records of '"+subdomain+"' found. Please specify record id! ")
            id = record.find("id").text
    conn.close()
    if id:
        return id
    else:
        raise Exception("Record '"+subdomain+"' not found!")

def get_current_ip():
    """get current ip of """
    keys = ["login_email", "login_password", "domain_id"]
    record_id = params['record_id']
    _param = { k:v for k,v in params.items() if k in keys }
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/json"}
    conn = http.client.HTTPSConnection("dnsapi.cn")
    conn.request("POST", "/Record.List", urllib.parse.urlencode(_param), headers)
    response = conn.getresponse()
    etree = ElementTree.parse(response)
    cur_ip = None
    for record in  etree.findall("records/item"):
        if record.find("id").text == record_id:
            cur_ip = record.find("value").text
    conn.close()
    return cur_ip

def get_public_ip():
    """ get ip address from dnspod """
    if DEBUG: print( "getting ip address from dnspod...")
    sock = socket.create_connection(('ns1.dnspod.net', 6666))
    ip = sock.recv(16)
    sock.close()
    return ip

# def get_if_ip(ifname):
#     """Get ip address by interface, Linux ONLY"""
#     if DEBUG: print(( "getting ip address of", ifname))
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     return socket.inet_ntoa(fcntl.ioctl(
#             s.fileno(),
#             0x8915,  # SIOCGIFADDR
#             struct.pack('256s', ifname[:15])
#             )[20:24])

def parse_arg():
    parser = argparse.ArgumentParser(description="Update dns record on dnspod dynamically.")
    parser.add_argument( '-I', '--interval', help="Set test interval, default is 300 seconds." )
    parser.add_argument( '-i', '--interface', help="Set interface." )
    parser.add_argument( '-u','--username', help="Set login email." )
    parser.add_argument( '-p','--password', help="Set login password." )
    parser.add_argument( '-d','--domain', help="Set domain name." )
    parser.add_argument( '-s','-r','--subdomain', help="Set subdomain/record name." )
    parser.add_argument( '--domain-id', help="Set domain id." )
    parser.add_argument( '--record-id', help="Set record id." )
    parser.add_argument( '--debug',action="store_true", help="Show debug outputs." )
    return parser.parse_args()

if __name__ == '__main__':
    
    args = parse_arg()
    
    # confiure
    DEBUG = args.debug or False
    interval = args.interval or 300

    #Set domain name
    domain = args.domain or input("Domain name: ")
    params['sub_domain'] = params['sub_domain'] \
            or args.subdomain or input("Subomain: ") or "@"
    
    #Login info
    params['login_email'] = params['login_email'] \
            or args.username or input("E-mail: ")
    params['login_password'] = params['login_password'] \
            or args.password or getpass()
    
    #domain and record id
    params['domain_id'] = params['domain_id'] \
            or args.domain_id or get_domain_id(domain)
    params['record_id'] = params['record_id']  \
            or args.record_id or get_record_id()
    
    if args.interface:
        getip = lambda : get_if_ip(args.interface)
    else:
        getip = lambda : get_public_ip()

    if DEBUG:
        print(( "domain_name: ", params['sub_domain']+'.'+domain))
        print(( "domain id:", params['domain_id']))
        print(( "record id:", params['record_id']))
        print(( "interval: ", interval))
    
    current_ip = get_current_ip()
    while True:
        try:
            ip = getip()
            if DEBUG: print(( "ip:", ip))
            if DEBUG: print(( "record ip:", current_ip))
            if current_ip != ip:
                if ddns(ip):
                    current_ip = ip
        except Exception as e:
            print( e)
            pass
        time.sleep(interval)