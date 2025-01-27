#! /usr/bin/env python3

# $Id$
# Author: Guenter Milde
# Copyright: This module has been placed in the public domain.

"""
Test the 'code' directive in body.py with syntax_highlight = 'none'.
"""

from test import DocutilsTestSupport


def suite():
    s = DocutilsTestSupport.ParserTestSuite(
            suite_settings={'syntax_highlight': 'none'})
    s.generateTests(totest)
    return s


totest = {}

totest['code-parsing-none'] = [
["""\
.. code::

   This is a code block.
""",
"""\
<document source="test data">
    <literal_block classes="code" xml:space="preserve">
        This is a code block.
"""],
["""\
.. code:: python
  :number-lines: 7

  def my_function():
      '''Test the lexer.
      '''

      # and now for something completely different
      print(8/2)
""",
"""\
<document source="test data">
    <literal_block classes="code python" xml:space="preserve">
        <inline classes="ln">
             7 \n\
        def my_function():
        <inline classes="ln">
             8 \n\
            \'\'\'Test the lexer.
        <inline classes="ln">
             9 \n\
            \'\'\'
        <inline classes="ln">
            10 \n\
        \n\
        <inline classes="ln">
            11 \n\
            # and now for something completely different
        <inline classes="ln">
            12 \n\
            print(8/2)
"""],
["""\
.. code:: latex

  hello \\emph{world} % emphasize
""",
"""\
<document source="test data">
    <literal_block classes="code latex" xml:space="preserve">
        hello \\emph{world} % emphasize
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
