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

  def test_tag_default_query(self):
    """
    Test the tag_default_query function.
    """
    question_doc = {}
    question_doc['question'] = 'question'
    question_doc['subject'] = 'subject'
    question_doc['tags'] = 'tag1 tag2'
    query_string = ('{"query":{"bool":{"should":[{"match":{"question":' + 
                    '"question"}},{"match":{"tags":{"query":"tag1 tag2",' +
                    '"boost":2}}},{"match":{"subject":"subject"}}]}}}')
    self.assertEqual(
      json.loads(query_functions.tag_default_query(question_doc)),
      json.loads(query_string))


if __name__ == '__main__':
  unittest.main()