from click.testing import CliRunner
from gw_cli import run_subprocess, set_hostname, set_ipv4, set_mtu

import inspect


class GwCliTest(object):

    def test_run_subprocess_success(self):
        result = run_subprocess(args=['ls', '-la'])
        assert result.returncode == 0

    def test_run_subprocess_failure(self):
        result = run_subprocess(args=['ls', '-y'])
        assert result.returncode != 0

    def test_set_hostname_success(self):
        pass

    def test_set_hostname_failure(self):
        pass

    def test_set_ipv4_success(self):
        pass

    def test_set_ipv4_failure(self):
        pass

    def test_set_mtu_success(self):
        pass

    def test_set_mtu_failure(self):
        pass


if __name__ == '__main__':
    gw_test = GwCliTest()
    all_members = inspect.getmembers(gw_test, inspect.ismethod)
    for member in all_members:
        if member[0].startswith('test_'):
            member[1]()
