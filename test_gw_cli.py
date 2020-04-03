# -*- coding:utf-8 -*-
# @Script: test_gw_cli.py
# @Author: Andre Litty
# @Email: alittysw@gmail.com
# @Create At: 2020-03-21 13:41:33
# @Last Modified By: Andre Litty
# @Last Modified At: 2020-04-03 11:39:24
# @Description: Test cases for command line tool gw_cli.

from click.testing import CliRunner
from gw_commands import run_subprocess, InvalidArgumentException
from gw_cli import (
    set_hostname,
    set_ipv4,
    set_mtu,
    set_dhcp_server
)

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
            'etn0'
            ])
        self.assertEqual(result.exit_code, 0)

    def test_set_ipv4_failure_no_address(self):
        result = self.runner.invoke(set_ipv4, args=[
            '--netmask',
            '24',
            '--device',
            'etn0'
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
        self.assertEqual(result.exit_code, 0)

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

if __name__ == '__main__':
    unittest.main()