"""
Runs all of the tests for BindiBot.
"""

import sys
import unittest
sys.path.append('./src/')
sys.path.append('./test/')

from test_util import TestUtil
from test_util import TestQueryFunctions


def suite():
  """
  Generates the test suite for the tests for BindiBot.
  """
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestUtil))
  suite.addTest(unittest.makeSuite(TestQueryFunctions))
  return suite

if __name__ == '__main__':
  unittest.main()
