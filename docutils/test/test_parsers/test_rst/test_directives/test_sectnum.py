#! /usr/bin/env python3

# $Id$
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Tests for the 'sectnum' directive.
"""

from test import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s


totest = {}

totest['sectnum'] = [
["""\
.. sectnum::
""",
"""\
<document source="test data">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.parts.SectNum
             .details:
"""],
["""\
.. sectnum::
   :depth: 23
   :start: 42
   :prefix: A Prefix
   :suffix: A Suffix
""",
"""\
<document source="test data">
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.parts.SectNum
             .details:
               depth: 23
               prefix: 'A Prefix'
               start: 42
               suffix: 'A Suffix'
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
