# -*- coding:utf-8 -*-
# @Script: gw_cli.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-21 13:42:22
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-03-21 13:42:22
# @Description: Command Line Tool to configure local network and dhcp settings on linux based machines.

import click
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

@click.command()
@click.option('--address', help='IPv4 address to assign to device')
@click.option('--netmask', help='IPv4 netmask')
@click.option('--device', help='Device to assign the address to')
def set_ipv4(address, netmask, device):
    if len(address) == 0 or len(netmask) == 0 or len(device) == 0:
        raise InvalidArgumentException
    args = ['ip', 'addr', 'add', address, netmask, 'dev', device]
    result = run_subprocess(args=args)

@click.command()
@click.option('--mtu', help='MTU to assign to device')
@click.option('--device', help='Device to assign the MTU to')
def set_mtu(mtu, device):
    if len(mtu) == 0 or len(device) == 0:
        raise InvalidArgumentException
    args = ['ip', 'link', 'set', device, 'mtu', mtu]
    result = run_subprocess(args=args)

@click.command()
@click.option('--hostname', help='New hostname')
def set_hostname(hostname):
    if len(hostname) == 0:
        raise InvalidArgumentException
    args = ['hostnamectl', 'set-hostname', hostname]
    result = run_subprocess(args=args)

@click.command()
@click.option('--domainname', help='New domain name')
@click.option('--beginIpRange', help='Begin of IP range')
@click.option('--endIpRange', help='End of IP range')
@click.option('--leaseTime', help='Lease time as string')
def set_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time):
    if len(domainname) == 0
    or len(begin_ip_range) == 0
    or len(end_ip_range) == 0
    of len(lease_time) == 0:
        raise InvalidArgumentException
    dhcp_server_config = make_dhcp_server_config(begin_ip_range, end_ip_range, lease_time, domain_name)
    with open('etc/udhcp.conf', 'w') as udhcp_conf:
        udhcp_conf.write(dhcp_server_config)
    args = ['udhcp', '/etc/udhcp.conf']
    result = run_subprocess(args=args)

# TODO: Get information how to handle client mac and ip address settings for dhcp
@click.option('--clientMacAddress', help='MAC address of client')
@click.option('--clientIPAddress', help='IP address of client')
def set_dhcp_client(client_mac_address, client_ip_address):
    if len(client_mac_address) == 0
    or len(client_ip_address) == 0:
        raise InvalidArgumentException
    args = []
    result = run_subprocess(args=args)