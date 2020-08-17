# -*- coding:utf-8 -*-
# @Script: gw_cli.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-21 13:42:22
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-08-17 15:34:09
# @Description: Command Line Tool to configure local network and dhcp settings
# on linux based machines.

import click
import subprocess
import yaml
import os
import logging
import re
import textwrap
import signal


logging.basicConfig(
    filename='/tmp/gw.log',
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

IP_REX = 'inet [0-9]+.[0-9]+.[0-9]+.[0-9]+/[0-9]+'


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


def get_current_address(device='eth0'):
    try:
        addr = subprocess.run(
            ['ip', 'addr', 'show', device],
            check=True,
            capture_output=True
        )
        if addr.returncode != 0:
            return None
        addr = addr.stdout.decode()
        ipv4 = re.search(IP_REX, addr).group()
        ipv4 = ipv4.split(' ')[-1]
        return ipv4
    except Exception:
        return None


def run_subprocess(args=[]):
    if not args or len(args) == 0:
        raise EmptyArgsException()
    logger.info(f'Starting subprocess with {args}')
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as cpe:
        result = cpe
    except Exception as e:
        result = e
    if isinstance(result, Exception):
        logger.error(f'Got exception while running subprocess: {result}')
    else:
        logger.info('Subprocess completed sccessfully')
    return result


def make_dhcp_server_config(begin_ip_range, end_ip_range, lease_time,
                            domain_name):
    return textwrap.dedent(f"""\
    start {begin_ip_range}
    end {end_ip_range}
    min_lease {lease_time}
    option domain {domain_name}
    """)


def get_dhcp_server_config():
    if not os.path.isfile('/etc/udhcpd.conf'):
        return []
    with open('/etc/udhcpd.conf', 'r') as udhcp_conf:
        config = udhcp_conf.readlines()
    config = [line.strip() for line in config]
    return [line.split(' ')[-1] for line in config]


def change_hostname(hostname):
    logger.info(f'Setting new hostname {hostname}')
    if not hostname:
        logger.error(
            'Insufficient arguments provided raising InvalidArgumentException')
        raise InvalidArgumentException
    args = ['hostnamectl', 'set-hostname', hostname]
    return run_subprocess(args=args)


def change_mtu(mtu, device='eth0'):
    logger.info(f'Setting new mtu {mtu} on {device}')
    if not mtu\
            or not device:
        logger.error(
            'Insufficient arguments provided raising InvalidArgumentException')
        raise InvalidArgumentException
    args = ['ip', 'link', 'set', device, 'mtu', mtu]
    return run_subprocess(args=args)


def stop_dhcp_server_if_running():
    logger.info('Stopping udhcpd if running...')
    try:
        result = subprocess.run(
            ['ps', '-A'],
            check=True,
            capture_output=True
        )
        for line in result.stdout.splitlines():
            if 'udhcpd' in line.decode():
                pid = int(line.split(None, 1)[0])
                os.kill(pid, signal.SIGKILL)
    except Exception as e:
        logger.error(f'Error while killing udhcod: {e}')


def change_dhcp_server(domain_name, begin_ip_range, end_ip_range, lease_time):
    logger.info(
        f'Setting new dhcp server config with {domain_name}, {begin_ip_range},\
        {end_ip_range}, {lease_time}')
    if not domain_name\
            or not begin_ip_range\
            or not end_ip_range\
            or not lease_time:
        logger.error(
            'Insufficient arguments provided raising InvalidArgumentException')
        raise InvalidArgumentException
    dhcp_server_config = make_dhcp_server_config(
        begin_ip_range,
        end_ip_range,
        lease_time,
        domain_name
    )
    stop_dhcp_server_if_running()
    with open('/etc/udhcpd.conf', 'w') as udhcp_conf:
        udhcp_conf.write(dhcp_server_config)
    args = ['udhcpd', '/etc/udhcpd.conf']
    return run_subprocess(args=args)


def change_ipv4(address, netmask, device='eth0'):
    logger.info(
        f'Setting new network address {address}, {netmask} on {device}')
    if not address\
            or not netmask\
            or not device:
        logger.error(
            'Insufficient arguments provided raising InvalidArgumentException')
        raise InvalidArgumentException
    new_address = f'{address}/{netmask}'
    current_address = get_current_address(device=device)
    if current_address is not None:
        args = ['ip', 'addr', 'del', current_address, 'dev', device]
        run_subprocess(args=args)
    args = ['ip', 'addr', 'add', new_address, 'dev', device]
    return run_subprocess(args=args)


def process_yaml(yml):
    logger.info(f'Processing YAML file {yml}')
    if not os.path.isfile(yml):
        logger.error(f'{yml} does not exist')
        raise InvalidArgumentException
    try:
        with open(yml, 'r') as yml_file:
            config = yaml.safe_load(yml_file)
        logger.info('Successfully processed YAML file')
        return config
    except Exception as e:
        logger.error(f'Error while reading YAML file got: {e}')
        return None


def set_modem(con_name='mobile', operator_apn='internet', pin=None, user=None,
              password=None):
    logger.info('Setting up modem')
    args = ['nmcli', 'c', 'add', 'type', 'gsm', 'ifname', '*',
            'con-name', con_name, 'apn', operator_apn]
    if pin is not None:
        args.extend(['pin', pin])
    if user is not None and password is not None:
        args.extend(['username', user, 'password', password])
    setup_result = run_subprocess(args=args)
    if setup_result.returncode == 0:
        args = ['nmcli', 'c', 'up', con_name]
        return run_subprocess(args=args)
    else:
        logger.error('Error while setting up modem')
        return setup_result


@click.group()
def cli():
    click.echo('### GW-CLI ###')


@cli.command()
@click.option('--address', help='IPv4 address to assign to device')
@click.option('--netmask', help='IPv4 netmask supported formats: 99\
    (CIRD format) and 999.999.999.999 (long mask format)')
@click.option('--device', default='eth0', help='Device to assign the address')
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
    change_hostname(local_network.get('hostname'))
    change_ipv4(
        local_network.get('ipAddress'),
        local_network.get('subnetMask'),
        local_network.get('device')
    )
    change_mtu(
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


@cli.command()
@click.option('--apn', default='internet', help='APN the modem is set to')
@click.option('--name', default='mobile', help='Connection name')
@click.option('--pin', default=None, help='SIMs PIN')
@click.option('--user', default=None, help='Username')
@click.option('--password', default=None, help='Password')
def setup_modem(apn, name, pin, user, password):
    set_modem(
        con_name=name,
        operator_apn=apn,
        pin=pin,
        user=user,
        password=password
    )
