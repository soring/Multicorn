# -*- coding: utf-8 -*-
# This file is part of Dyko
# Copyright © 2008-2010 Kozea
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Kalamar.  If not, see <http://www.gnu.org/licenses/>.

"""
XML test.

Test the XML backend.

"""

import tempfile
import shutil

from nose.tools import eq_
from kalamar.access_point.filesystem import FileSystem, FileSystemProperty
from kalamar.access_point.xml import XML, XMLProperty
from kalamar.site import Site
from ..common import run_common, make_site


class TemporaryDirectory(object):
    """Utility class for the tests."""
    def __init__(self):
        self.directory = None

    def __enter__(self):
        self.directory = tempfile.mkdtemp()
        return self.directory

    def __exit__(self, exit_type, value, traceback):
        shutil.rmtree(self.directory)

def test_serialization():
    def xml_content_test(site):
        item = site.open('things', {'id': 1})
        eq_(item['stream'].read(), "<foo><bar><baz>foo</baz></bar></foo>")
    runner(xml_content_test)

def test_update_document():
    def xml_update_test(site):
        item = site.open('things', {'id': 1})
        item['name'] = 'updated name'
        item.save()
        item = site.open('things', {'id': 1})
        eq_(item['stream'].read(), "<foo><bar><baz>update name</baz></bar></foo>")

def test_shared_structure():
    with TemporaryDirectory() as temp_dir:
        file_ap = make_file_ap(temp_dir)
        access_point = XML(file_ap, [
            ('name' , XMLProperty(unicode, '//bar/name')),
            ('color', XMLProperty(unicode, '//bar/color'))],
            'stream',
            'foo')
        site = Site()
        site.register('test', access_point)
        item = site.create('test', {
            'name': 'hulk',
            'color': 'green',
            'id': 1})
        item.save()
        item = site.open('test', {'id': 1})
        eq_(item['stream'].read(), "<foo><bar><name>hulk</name><color>green</color></bar></foo>")

def make_file_ap(temp_dir):
    return FileSystem( temp_dir,
            "(.*)\.txt", [("id", FileSystemProperty(int))],
            content_property="stream")


# Common tests

def runner(test):
    """Test runner for ``test``."""
    with TemporaryDirectory() as temp_dir:
        file_access_point = make_file_ap(temp_dir)
        access_point = XML(file_access_point, [('name',
            XMLProperty(unicode, '//bar/baz')),], 'stream', 'foo')
        site = make_site(access_point, fill=not hasattr(test, "nofill"))
        test(site)

@run_common
def test_xml_common():
    """Define a custom test runner for the common tests."""
    return None, runner, "xml"
