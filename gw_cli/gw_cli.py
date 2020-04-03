# -*- coding:utf-8 -*-
# @Script: gw_cli.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-21 13:42:22
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-04-03 11:52:42
# @Description: Command Line Tool to configure local network and dhcp settings on linux based machines.

import click
import gw_commands

@click.group()
def cli():
    click.echo('### GW-CLI ###')

@cli.command()
@click.option('--address', help='IPv4 address to assign to device')
@click.option('--netmask', help='IPv4 netmask')
@click.option('--device', help='Device to assign the address to')
def set_ipv4(address, netmask, device):
    gw_commands.set_ipv4(address, netmask, device)

@cli.command()
@click.option('--mtu', help='MTU to assign to device')
@click.option('--device', help='Device to assign the MTU to')
def set_mtu(mtu, device):
    gw_commands.set_mut(mtu, device)

@cli.command()
@click.option('--hostname', help='New hostname')
def set_hostname(hostname):
    gw_commands.set_hostname(hostname)

@cli.command()
@click.option('--domain-name', help='New domain name')
@click.option('--begin-ip-range', help='Begin of IP range')
@click.option('--end-ip-range', help='End of IP range')
@click.option('--lease-time', help='Lease time as string')
def set_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time):
    gw_commands.set_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time)
