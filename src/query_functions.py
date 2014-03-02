"""
Query functions to be passed to top_answers module.
Each query will score results differently.
"""

import json


def default_match_query(question_doc):
  """Returns the query string to search for related posts."""
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