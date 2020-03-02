import click
import subprocess


class InvalidArgumentException(Exception):
    pass

def run_subprocess(args=[]):
    if not args or len(args) == 0:
        raise InvalidArgumentException()
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

@click.command()
@click.option('--address', help='IPv4 address to assign to device')
@click.option('--netmask', help='IPv4 netmask')
@click.option('--device', help='Device to assign the address to')
def set_ipv4(address, netmask, device):
    try:
        args = ['ip', 'addr', 'add', address, netmask, 'dev', device]
        result = run_subprocess(args=args)
    except InvalidArgumentException:
        pass

@click.command()
@click.option('--mtu', help='MTU to assign to device')
@click.option('--device', help='Device to assign the MTU to')
def set_mtu(mtu, device):
    try:
        args = ['ip', 'link', 'set', device, 'mtu', mtu]
        result = run_subprocess(args=args)
    except InvalidArgumentException:
        pass

@click.command()
@click.option('--hostname', help='New hostname')
def set_hostname(hostname):
    try:
        args = ['hostnamectl', 'set-hostname', hostname]
        result = run_subprocess(args=args)
    except InvalidArgumentException:
        pass

