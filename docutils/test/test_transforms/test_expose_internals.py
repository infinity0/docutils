#! /usr/bin/env python3

# $Id$
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Test module for universal.ExposeInternals transform.
"""

from test import DocutilsTestSupport  # before importing docutils!
from docutils.transforms.universal import ExposeInternals
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(
        parser, suite_settings={'expose_internals': ['rawsource', 'source']})
    s.generateTests(totest)
    return s


totest = {}

totest['transitions'] = ((ExposeInternals,), [
["""\
This is a test.
""",
"""\
<document internal:rawsource="" source="test data">
    <paragraph internal:rawsource="This is a test." internal:source="test data">
        This is a test.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
