"""
Test cases for query_functions.py.
"""

import json
import unittest

import query_functions


class TestQueryFunctions(unittest.TestCase):
  """
  Test cases for query_functions.py.
  """
  def test_default_match_query(self):
    """
    Test the default_match_query function.
    """
    question_doc = {}
    question_doc['question'] = 'question'
    question_doc['subject'] = 'subject'
    query_string = ('{"query":{"bool":{"should":[{"match":{"question":' + 
                    '"question"}},{"match":{"subject":"subject"}}]}}}')
    self.assertEqual(
      json.loads(query_functions.default_match_query(question_doc)),
      json.loads(query_string))


if __name__ == '__main__':
  unittest.main()