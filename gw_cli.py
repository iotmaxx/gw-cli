# -*- coding:utf-8 -*-
# @Script: gw_cli.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-21 13:42:22
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-11-09 02:20:45
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
import time
import configparser
from ipaddress import IPv4Network


logging.basicConfig(
    filename='/tmp/gw.log',
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

IP_REX = 'inet [0-9]+.[0-9]+.[0-9]+.[0-9]+/[0-9]+'
file_path_systemd_config = '/etc/systemd/network/10-eth0.network'
file_path_unmanaged = '/etc/NetworkManager/conf.d/unmanaged.conf'


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
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(file_path_systemd_config)
    
    start = config['DHCPServer']['PoolOffset']
    end = config['DHCPServer']['PoolSize']
    lease_time = 7200
    domain_name = "Gateway"
    isDHCPServer = config['Network']['DHCPServer']

    dhcp_config = [start, end, lease_time, domain_name, isDHCPServer]

    return dhcp_config    


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


def swap_dhcp_state(flag=True):
    if flag:
        dhcp_dict = {'DHCP': 'false', 'DHCPServer':'true'}
    else:
        dhcp_dict = {'DHCP': 'true', 'DHCPServer':'false'}

    change_hostvalues(dhcp_dict, 'Network')

    #stop_dhcp_server_if_running()   
    args = ['systemctl', 'restart', 'NetworkManager']
    run_subprocess(args=args)



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


    dhcp_dict = {'PoolOffset': begin_ip_range, 'PoolSize':end_ip_range}

    change_hostvalues(dhcp_dict, 'DHCPServer')

    #stop_dhcp_server_if_running()   
    args = ['systemctl', 'restart', 'NetworkManager']
    run_subprocess(args=args)


def change_ipv4(address, netmask, device='eth0'):
    logger.info(
        f'Setting new network address {address}, {netmask} on {device}')
    if not address\
            or not netmask\
            or not device:
        logger.error(
            'Insufficient arguments provided raising InvalidArgumentException')
        raise InvalidArgumentException
    address_digit = "0.0.0.0/{1}".format(address, netmask)
    netmask_bits = IPv4Network(address_digit).prefixlen
    

    new_address = "{0}/{1}".format(address, netmask_bits)
    #new_address = f'{address}/{netmask}'
    current_address = get_current_address(device=device)



    ipv4_dict = {'Address':new_address}

    change_hostvalues(ipv4_dict, 'Network')

    change_unmanaged_state(True)

    args = ['systemctl', 'restart', 'NetworkManager']
    run_subprocess(args=args)

    args = ['nmcli', 'con', 'mod', 'eth0', 'ipv4.address', new_address]
    run_subprocess(args=args)

    change_unmanaged_state(False)

    args = ['systemctl', 'restart', 'NetworkManager']
    run_subprocess(args=args)

   
def config_handler(operator_apn='internet', pin=None, autoreconnect=False, user = None, password= None):
    path = '/config/ModemConfig'
    if not os.path.isfile(path):
        config = configparser.ConfigParser()
        config.optionxform = str
        config['Modem'] = {
            'Apn': operator_apn,
            'Pin': pin,
            'User': 'user',
            'Password': 'password',
            'Autoreconnect': autoreconnect
        }
        configfile = open(path, 'w')
        config.write(configfile, space_around_delimiters=False)
        configfile.close()
    else:
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(path)
        config.set('Modem', 'Apn', operator_apn)
        config.set('Modem', 'Pin', str(pin))
        if user is None:
            config.set('Modem', 'User', 'user')
        if password is None:
            config.set('Modem', 'Password', 'password')
        
        config.set('Modem', 'Autoreconnect', str(autoreconnect))
        configfile = open(path, 'w')
        config.write(configfile, space_around_delimiters=False)
        configfile.close()

def autostart():
    time.sleep(30)
    path = '/config/ModemConfig'
    os.path.exists('/dev/ttyUSB0')
    for x in range(3):
        if os.path.exists('/dev/ttyUSB0'):
            if os.path.isfile(path):
                config = configparser.ConfigParser()
                config.optionxform = str
                config.read(path)
                if config.getboolean('Modem','Autoreconnect'):
                    set_modem(operator_apn=config['Modem']['Apn'], pin=config['Modem']['Pin'], user=config['Modem']['User'], password=config['Modem']['Password'])
                    break
        else:
            time.sleep(3)


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
    
    if pin:
        args_pin = ['mmcli', '-i', '0', '--pin', pin]
        run_subprocess(args=args_pin)
        time.sleep(2)
    args = ['nmcli', 'c', 'add', 'type', 'gsm', 'ifname', '*',
            'con-name', con_name, 'apn', operator_apn]
    config_handler(operator_apn=operator_apn, pin=pin, autoreconnect=True, user = None, password= None)
    setup_result = run_subprocess(args=args)
    args = ['nmcli', 'c', 'up', con_name]
    return run_subprocess(args=args)



def change_hostvalues(valueDict, section):
    args = ['mount', '-o', 'remount,rw', '/']
    run_subprocess(args=args)    

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(file_path_systemd_config)
    for key in valueDict:
        config.set(section, key, valueDict[key]) 

    cfgfile = open(file_path_systemd_config,'w')
    config.write(cfgfile, space_around_delimiters=False)  
    cfgfile.close()  
    args = ['mount', '-o', 'remount,ro', '/']
    run_subprocess(args=args)     


def change_unmanaged_state(flag):
    args = ['mount', '-o', 'remount,rw', '/']
    run_subprocess(args=args)
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(file_path_unmanaged)
    if flag is True:    
        config.set('keyfile', 'unmanaged-devices', 'None')
    else:
        config.set('keyfile', 'unmanaged-devices', 'interface-name:eth0')

    cfgfile = open(file_path_unmanaged,'w')
    config.write(cfgfile, space_around_delimiters=True)  
    cfgfile.close()  
    args = ['mount', '-o', 'remount,ro', '/']
    run_subprocess(args=args)

if __name__ == "__main__":
    autostart()


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
    modem_config = config.get('modem')
    set_modem(
        con_name=modem_config.get('conName'),
        operator_apn=modem_config.get('operatorApn'),
        pin=modem_config.get('pin', None),
        user=modem_config.get('user', None),
        password=modem_config.get('password', None)
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
