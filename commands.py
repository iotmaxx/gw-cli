# -*- coding:utf-8 -*-
# @Script: commands.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-04-03 11:15:51
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-04-03 11:30:16
# @Description: Commands.

import subprocess


class EmptyArgsException(Exception):
    
    def __init__(self, message='The passed arguments were empty'):
        self.message = message
    
    def __str__(self):
        return self.message

class InvalidArgumentException(Exception):
    
    def __init__(self, message='The passed argument wasn\'t valid'):
        self.message = message
    
    def __str__(self):
        return self.message

def run_subprocess(args=[]):
    if not args or len(args) == 0:
        raise EmptyArgsException()
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            check=True
            )
    except subprocess.CalledProcessError as cpe:
        result = cpe
    except Exception as e:
        result = None
    return result

def make_dhcp_server_config(begin_ip_range, end_ip_range, lease_time, domain_name):
    return f"""
    start {begin_ip_range}
    end {end_ip_range}
    min_lease {lease_time}
    option domain {domain_name}
    """

def get_dhcp_server_config():
    if not os.path.isfile('etc/udhcp.conf'):
        return []
    with open('etc/udhcp.conf', 'r') as udhcp_conf:
        config = udhcp_conf.readlines()
    config = [line.strip() for line in config]
    return [line.split(' ')[-1] for line in config]

def set_hostname(hostname):
    if not hostname:
        raise InvalidArgumentException
    args = ['hostnamectl', 'set-hostname', hostname]
    return run_subprocess(args=args)

def set_mut(mtu, device):
    if not mtu\
    or  not device:
        raise InvalidArgumentException
    args = ['ip', 'link', 'set', device, 'mtu', mtu]
    return run_subprocess(args=args)

def set_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time):
    if not domain_name\
    or not begin_ip_range\
    or not end_ip_range\
    or not lease_time:
        raise InvalidArgumentException
    dhcp_server_config = make_dhcp_server_config(begin_ip_range, end_ip_range, lease_time, domain_name)
    with open('etc/udhcp.conf', 'w') as udhcp_conf:
        udhcp_conf.write(dhcp_server_config)
    args = ['udhcp', '/etc/udhcp.conf']
    return run_subprocess(args=args)

def set_ipv4(address, netmask, device):
    if not address\
    or not netmask\
    or not device:
        raise InvalidArgumentException
    args = ['ip', 'addr', 'add', address, netmask, 'dev', device]
    result = run_subprocess(args=args)
