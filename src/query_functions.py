"""
Query functions to be passed to top_answers module.
Each query will score results differently.
"""

import json


def default_match_query(question_doc):
  """
  Returns the query string to search for related posts.
  """
  question = question_doc['question'][:1000] # limit query length
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

def tag_match_query_1(question_doc):
  """
  Returns the query string to search for related posts with tag limitation with
  a boost of 1 on the tag.
  """
  question = question_doc['question'][:1000] # limit query length
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
            'match' : {'tags': {'query':tags, 'boost':1}}
          }
        ]
      }
    }
  }
  if subject:
    query_dict['query']['bool']['should'].append({'match':{'subject':subject}})
  return json.dumps(query_dict)

def tag_match_query_2(question_doc):
  """
  Returns the query string to search for related posts with tag limitation with
  a boost of 2 on the tag.
  """
  question = question_doc['question'][:1000] # limit query length
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
            'match' : {'tags': {'query':tags, 'boost':2}}
          }
        ]
      }
    }
  }
  if subject:
    query_dict['query']['bool']['should'].append({'match':{'subject':subject}})
  return json.dumps(query_dict)

def tag_match_query_3(question_doc):
  """
  Returns the query string to search for related posts with tag limitation with
  a boost of 3 on the tag.
  """
  question = question_doc['question'][:1000] # limit query length
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

def tag_match_query_100(question_doc):
  """
  Returns the query string to search for related posts with tag limitation with
  a boost of 100 on the tag.
  """
  question = question_doc['question'][:1000] # limit query length
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
            'match' : {'tags': {'query':tags, 'boost':100}}
          }
        ]
      }
    }
  }
  if subject:
    query_dict['query']['bool']['should'].append({'match':{'subject':subject}})
  return json.dumps(query_dict)

def answer_match_query(question_doc):
  """
  Return the query string to search for related posts by also comparing the
  question text to the answer.
  """
  question = question_doc['question'][:1000] # limit query length
  subject = question_doc['subject']
  query_dict = {
    'query': {
      'bool': {
        'should': [
          {
            'match' : {'question' : question}
          },
          {
            'match' : {'answer': question}
          },
          {
            'match' : {'subject': subject}
          }
        ]
      }
    }
  }
  return json.dumps(query_dict)

def answer_tag_match_query(question_doc):
  """
  Return the query string to search for related posts by also comparing the
  query text to answer and filtering by tags.
  """
  question = question_doc['question'][:1000] # limit query length
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
            'match' : {'answer': question}
          },
          {
            'match' : {'subject': subject}
          },
          {
            'match' : {'tags': {'query':tags, 'boost':3}}
          }
        ]
      }
    }
  }
  return json.dumps(query_dict)


# Dictionary that contains all query functions for simple importing.
query_functions = {
  'default_match_query': default_match_query,
  'tag_match_query_1': tag_match_query_1,
  'tag_match_query_2': tag_match_query_2,
  'tag_match_query_3': tag_match_query_3,
  'tag_match_query_100': tag_match_query_100,
  'answer_match_query': answer_match_query,
  'answer_tag_match_query': answer_tag_match_query,
}