# -*- coding:utf-8 -*-
# @Script: test_gw_cli.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-21 13:41:33
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-08-06 16:47:15
# @Description: Test cases for command line tool gw_cli.
import unittest
import tempfile

from click.testing import CliRunner
from gw_cli import (
    run_subprocess,
    InvalidArgumentException,
    set_hostname,
    set_ipv4,
    set_mtu,
    set_dhcp_server,
    process_yaml,
    setup_modem
)


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
        self.assertEqual(result.exit_code, 0)

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
            'eth0'
        ])
        self.assertEqual(result.exit_code, 0)

    def test_set_ipv4_failure_no_address(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--netmask',
            '24',
            '--device',
            'eth0'
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_ipv4_failure_empty_address(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '',
            '--netmask',
            '24',
            '--device',
            'eth0'
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_ipv4_failure_no_netmask(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--address',
            '127.0.0.2',
            '--netmask',
            '--device',
            'eth0'
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
            'eth0'
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
            'eth0'
        ])
        self.assertEqual(result.exit_code, 0)

    def test_set_mtu_failure_no_mtu(self):
        result = self.runner.invoke(set_mtu, args=[
            '--mtu',
            '--device',
            'eth0'
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, SystemExit)

    def test_set_mtu_failure_empty_mtu(self):
        result = self.runner.invoke(set_mtu, args=[
            '--mtu',
            '',
            '--device',
            'eth0'
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

    def test_set_dhcp_server_success(self):
        result = self.runner.invoke(set_dhcp_server, args=[
            '--domain-name',
            'local',
            '--begin-ip-range',
            '127.0.0.1',
            '--end-ip-range',
            '127.0.0.10',
            '--lease-time',
            5000
        ])
        self.assertEqual(result.exit_code, 0)

    def test_set_dhcp_server_failure_no_domain(self):
        result = self.runner.invoke(set_dhcp_server, args=[
            '--domain-name',
            '',
            '--begin-ip-range',
            '127.0.0.1',
            '--end-ip-range',
            '127.0.0.10',
            '--lease-time',
            5000
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_dhcp_server_failure_no_begin_ip_range(self):
        result = self.runner.invoke(set_dhcp_server, args=[
            '--domain-name',
            'local',
            '--begin-ip-range',
            '',
            '--end-ip-range',
            '127.0.0.10',
            '--lease-time',
            5000
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_dhcp_server_failure_no_end_ip_range(self):
        result = self.runner.invoke(set_dhcp_server, args=[
            '--domain-name',
            'local',
            '--begin-ip-range',
            '127.0.0.1',
            '--end-ip-range',
            '',
            '--lease-time',
            5000
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_set_dhcp_server_failure_no_lease_time(self):
        result = self.runner.invoke(set_dhcp_server, args=[
            '--domain-name',
            'local',
            '--begin-ip-range',
            '127.0.0.1',
            '--end-ip-range',
            '127.0.0.10',
            '--lease-time',
            ''
        ])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIsInstance(result.exception, InvalidArgumentException)

    def test_process_yaml_success(self):
        result = process_yaml('yaml_template.yml')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_process_yaml_failure_file_not_found(self):
        self.assertRaises(InvalidArgumentException,
                          process_yaml, 'invalid_file.yml')

    def test_process_yaml_failure_invalid_yaml(self):
        with open('yaml_template.yml', 'r') as original_yaml:
            content = original_yaml.read()
        content = content + 'some silly content'
        temp_yaml = tempfile.NamedTemporaryFile()
        temp_yaml.write(content.encode())
        result = process_yaml(temp_yaml.name)
        self.assertIsNone(result)

    def test_set_modem_success(self):
        result = self.runner.invoke(setup_modem, args=[
            '--apn',
            'internet',
            '--name',
            'mobile'
        ])
        self.assertEqual(result.exit_code, 0)

    def test_set_modem_failure_wrong_apn(self):
        result = self.runner.invoke(setup_modem, args=[
            '--apn',
            'false_internet',
            '--name',
            'mobile'
        ])
        self.assertNotEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()
