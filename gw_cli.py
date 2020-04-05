# -*- coding:utf-8 -*-
# @Script: gw_cli.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-21 13:42:22
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-04-05 15:40:42
# @Description: Command Line Tool to configure local network and dhcp settings on linux based machines.

import click
import subprocess
import yaml
import os

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

def change_hostname(hostname):
    if not hostname:
        raise InvalidArgumentException
    args = ['hostnamectl', 'set-hostname', hostname]
    return run_subprocess(args=args)

def change_mtu(mtu, device):
    if not mtu\
    or  not device:
        raise InvalidArgumentException
    args = ['ip', 'link', 'set', device, 'mtu', mtu]
    return run_subprocess(args=args)

def change_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time):
    if not domain_name\
    or not begin_ip_range\
    or not end_ip_range\
    or not lease_time:
        raise InvalidArgumentException
    dhcp_server_config = make_dhcp_server_config(
        begin_ip_range,
        end_ip_range,
        lease_time,
        domain_name
        )
    with open('etc/udhcp.conf', 'w') as udhcp_conf:
        udhcp_conf.write(dhcp_server_config)
    args = ['udhcp', '/etc/udhcp.conf']
    return run_subprocess(args=args)

def change_ipv4(address, netmask, device):
    if not address\
    or not netmask\
    or not device:
        raise InvalidArgumentException
    args = ['ip', 'addr', 'add', address, netmask, 'dev', device]
    result = run_subprocess(args=args)

def process_yaml(yml):
    if not os.path.isfile(yml):
        raise InvalidArgumentException
    try:
        with open(yml, 'r') as yml_file:
            config = yaml.safe_load(yml_file)
        return config
    except Exception:
        return None

@click.group()
def cli():
    click.echo('### GW-CLI ###')

@cli.command()
@click.option('--address', help='IPv4 address to assign to device')
@click.option('--netmask', help='IPv4 netmask')
@click.option('--device', default='eth0', help='Device to assign the address to')
def set_ipv4(address, netmask, device):
    change_ipv4(address, netmask, device)

@cli.command()
@click.option('--mtu', help='MTU to assign to device')
@click.option('--device', default='eth0', help='Device to assign the MTU to')
def set_mtu(mtu, device):
    change_mtu(mtu, device)

@cli.command()
@click.option('--hostname', help='New hostname')
def set_hostname(hostname):
    change_hostname(hostname)

@cli.command()
@click.option('--domain-name', help='New domain name')
@click.option('--begin-ip-range', help='Begin of IP range')
@click.option('--end-ip-range', help='End of IP range')
@click.option('--lease-time', help='Lease time as string')
def set_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time):
    change_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time)

@cli.command()
@click.option('--yml', default='yaml_template.yml', help='YAML file to load')
def load_from_yaml(yml):
    config = process_yaml(yml)
    if not config:
        return
    local_network = config.get('localNetwork')
    set_hostname(local_network.get('hostname'))
    set_ipv4(
        local_network.get('ipAddress'),
        local_network.get('subnetMask'),
        local_network.get('device')
    )
    set_mtu(
        local_network.get('mtu'),
        local_network.get('device')
    )
    dhcp_server = config.get('dhcpServer')
    change_dhcp_server(
        dhcp_server.get('domainName'),
        dhcp_server.get('beginIpRange'),
        dhcp_server.get('endIpRange'),
        dhcp_server.get('leaseTime')
    )
