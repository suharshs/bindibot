"""
Query functions to be passed to top_answers module.
Each query will score results differently.
Possible query functions are:
'default_match_query'
'tag_default_query'
"""

import json


def default_match_query(question_doc):
  """
  Returns the query string to search for related posts.
  """
  question = question_doc['question']
  subject = question_doc['subject']
  query_dict = {
    'query': {
      'bool': {
        'should': [
          {
            'match' : {'question' : question}
          }
        ]
      }
    }
  }
  if subject:
    query_dict['query']['bool']['should'].append({'match':{'subject':subject}})
  return json.dumps(query_dict)

def tag_default_query(question_doc):
  """
  Returns the query string to search for related posts with tag limitation.
  """
  question = question_doc['question']
  subject = question_doc['subject']
  tags = question_doc['tags']
  query_dict = {
    'query': {
      'bool': {
        'should': [
          {
            'match' : {'question' : question}
          },
          {
            'match' : {'tags': {'query':tags, 'boost':3}}
          }
        ]
      }
    }
  }
  if subject:
    query_dict['query']['bool']['should'].append({'match':{'subject':subject}})
  return json.dumps(query_dict)


# Dictionary that contains all query functions for simple importing.
query_functions = {
  'default_match_query': default_match_query,
  'tag_default_query': tag_default_query
}