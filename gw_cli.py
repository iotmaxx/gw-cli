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

