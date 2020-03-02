from click.testing import CliRunner
from gw_cli import run_subprocess, set_hostname, set_ipv4, set_mtu, InvalidArgumentException

import unittest

class TestGwCli(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()
    
    def test_run_subprocess_success(self):
        result = run_subprocess(args=['ls', '-la'])
        self.assertEqual(result.returncode, 0)

    def test_run_subprocess_failure(self):
        result = run_subprocess(args=['ls', '-y'])
        self.assertNotEqual(result.returncode, 0)

    def test_set_hostname_success(self):
        result = self.runner.invoke(set_hostname, args=[
            '--hostname',
            'new_hostname'
            ])
        self.assertEqual(result.returncode, 0)

    def test_set_hostname_failure_no_hostname(self):
        result = self.runner.invoke(set_hostname, args=[
            '--hostname'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)

    def test_set_hostname_failure_empty_hostname(self):
        result = self.runner.invoke(set_hostname, args=[
            '--hostname',
            ''
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_ipv4_success(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '127.0.0.2',
            '--netmask',
            '24',
            '--device',
            'etn0'
            ])
        self.assertEqual(result.returncode, 0)

    def test_set_ipv4_failure_no_address(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--netmask',
            '24',
            '--device',
            'etn0'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)

    def test_set_ipv4_failure_empty_address(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '',
            '--netmask',
            '24',
            '--device',
            'etn0'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_ipv4_failure_no_netmask(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '127.0.0.2',
            '--netmask',
            '--device',
            'etn0'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)

    def test_set_ipv4_failure_empty_netmask(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '127.0.0.2',
            '--netmask',
            '',
            '--device',
            'etn0'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_ipv4_failure_no_device(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '127.0.0.2',
            '--netmask',
            '24',
            '--device'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)

    def test_set_ipv4_failure_empty_device(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '127.0.0.2',
            '--netmask',
            '24',
            '--device',
            ''
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_mtu_success(self):
        result = self.runner.invoke(set_mtu, args=[
            '--mtu',
            '2200',
            '--device',
            'etn0'
            ])
        self.assertEqual(result.returncode, 0)

    def test_set_mtu_failure_no_mtu(self):
        result = self.runner.invoke(set_mtu, args=[
            '--mtu',
            '--device',
            'etn0'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)

    def test_set_mtu_failure_empty_mtu(self):
        result = self.runner.invoke(set_mtu, args=[
            '--mtu',
            '',
            '--device',
            'etn0'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_mtu_failure_no_device(self):
        result = self.runner.invoke(set_mtu, args=[
            '--mtu',
            '2020',
            '--device'
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)

    def test_set_mtu_failure_empty_device(self):
        result = self.runner.invoke(set_mtu, args=[
            '--mtu',
            '2020',
            '--device',
            ''
            ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

if __name__ == '__main__':
    unittest.main()