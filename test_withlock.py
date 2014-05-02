#!/usr/bin/env python

# Copyright 2014 Open Source Robotics Foundation

# 
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
# 
#        http://www.apache.org/licenses/LICENSE-2.0
# 
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import os
import subprocess
import shutil
import tempfile
import time
import unittest


class TempDirLockfile():
    def __enter__(self):
        self.dir = tempfile.mkdtemp(prefix=os.path.expanduser('~')+'/')
        return os.path.join(self.dir, 'lockfile')

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.dir)


class TestWithlock(unittest.TestCase):

    def test_basic(self):
        """ Check for basic functionality """
        with TempDirLockfile() as lf:
            cmd = "./withlock %s echo hello world" % lf
            self.assertEqual(subprocess.call(cmd.split()), 0)

    def test_version(self):
        """ Check for not crashing """
        cmd = "./withlock --version"
        self.assertEqual(subprocess.call(cmd.split()), 0)

    def test_help(self):
        """ Check for not crashing """
        cmd = "./withlock --help"
        self.assertEqual(subprocess.call(cmd.split()), 0)

    def test_group_writeable(self):
        """ Test a group writable location for protection """
        cmd = "./withlock /tmp/lockfile echo hello world"
        self.assertEqual(subprocess.call(cmd.split()), 3)

    def test_trylock(self):
        with TempDirLockfile() as lf:
            cmd = "./withlock %s sleep 5" % lf
            p = subprocess.Popen(cmd.split())
            # make sure the above has started
            time.sleep(0.1)
            cmd = "./withlock %s echo hello world" % lf
            retval = subprocess.call(cmd.split())
            p.kill()
            self.assertEqual(retval, 1)

    def test_trylock_quiet(self):
        with TempDirLockfile() as lf:
            cmd = "./withlock %s sleep 5" % lf
            p = subprocess.Popen(cmd.split())
            # make sure the above has started
            time.sleep(0.1)
            cmd = "./withlock -q %s echo hello world" % lf
            retval = subprocess.call(cmd.split())
            p.kill()
            self.assertEqual(retval, 0)

    def test_timeout(self):
        with TempDirLockfile() as lf:
            cmd = "./withlock %s sleep 5" % lf
            p = subprocess.Popen(cmd.split())
            # make sure the above has started
            time.sleep(0.1)
            cmd = "./withlock -w 2 %s echo hello world" % lf
            start_time = time.time()
            retval = subprocess.call(cmd.split())
            p.kill()
            self.assertEqual(retval, 1)
            delta = time.time() - start_time
            self.assertTrue(2.0 <= delta)
            self.assertTrue(delta < 3.0)
