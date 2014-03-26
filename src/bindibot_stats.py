"""
Runs bindibot versions on fixed test data and outputs results.
"""

import argparse
from elasticsearch import Elasticsearch
from top_answers import get_answers
from query_functions import query_functions
from populate_test_data import UniqueQuestionsIterator


def is_valid_answer(question_id, answer_id, es, es_index, es_type):
  query_string = """
  {
  "query": {
    "bool" : {
      "must" : [
        {
          "term" : {"c_id": "%s"}
        },
        {
          "term" : {"answer_id": "%s"}
        }
      ]
    }
  }
  }
  """ % (question_id, answer_id.lower())

  search_results = es.search(es_index, es_type, body=query_string, size=1)
  return search_results['hits']['total'] > 0

def get_question_doc(current_id, es, es_index, es_type):
  query_string = """
{"query" : { "query_string" : {"query" : "%s","fields":["c_id"]} }}
""" % current_id

  search_results = es.search(es_index, es_type, body=query_string, size=1)
  return search_results['hits']['hits'][0]['_source']


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Structure raw json data.')
  parser.add_argument('--es_test_host',
                      help='Read test data from elasticsearch.', required=True)
  parser.add_argument('--es_test_index',
                      help='Read test data from this index.', required=True)
  parser.add_argument('--es_test_type',
                      help='Read test data from this type.', required=True)
  parser.add_argument('--es_test_question_host',
                      help='Read test questions from elasticsearch.',
                      required=True)
  parser.add_argument('--es_test_question_index',
                      help='Read test questions from this index.',
                      required=True)
  parser.add_argument('--es_test_question_type',
                      help='Read test questions from this type.', required=True)
  parser.add_argument('--es_question_host',
                      help='Read question data from elasticsearch.',
                      required=True)
  parser.add_argument('--es_question_index',
                      help='Read question data from this index.',
                      required=True)
  parser.add_argument('--es_question_type',
                      help='Read question data from this type.',
                      required=True)
  args = parser.parse_args()

  test_question_es = Elasticsearch([args.es_test_question_host])
  test_valid_pairs_es = Elasticsearch([args.es_test_host])

  test_iterator = UniqueQuestionsIterator(
      [args.es_test_host], args.es_test_index, args.es_test_type)
  current_id = test_iterator.next()

  total = 0
  correct = dict([(func, 0) for func in query_functions.keys()])

  while current_id is not None:
    question_doc = get_question_doc(current_id, test_question_es,
                                    args.es_test_question_index,
                                    args.es_test_question_type)
    for func in query_functions.keys():
      answer_id = get_answers([args.es_question_host], args.es_question_index,
                              args.es_question_type, question_doc, 1,
                              query_functions[func])[0][0]
      total += 1
      if is_valid_answer(current_id, answer_id, test_valid_pairs_es,
                         args.es_test_index, args.es_test_type):
        correct[func] += 1
    current_id = test_iterator.next()

  print correct
