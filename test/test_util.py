"""
Test cases for util.py.
"""

from datetime import datetime
import math
from mock import Mock
import unittest

import util


# Mocks
class MockDateTime(datetime):
  @classmethod
  def now(cls):
    return datetime(2000,1,1)

util.datetime = MockDateTime
util.randint = Mock(return_value=123456789)


class TestUtil(unittest.TestCase):
  """
  Test cases for util.py.
  """
  def test_to_base36(self):
    """
    Test the to_base36 function.
    """
    self.assertEqual(util.to_base36(123456789), '21i3v9')

  def test_js_getTime(self):
    """
    Test the js_getTime function.
    """
    self.assertTrue(math.fabs(util.js_getTime() - 946706400000) < 1000000000)


if __name__ == '__main__':
  unittest.main()