"""
Runs bindibot on the chosen test questions.
"""

import argparse
from elasticsearch import Elasticsearch
from top_answers import get_answers
from query_functions import query_functions
from structure_question_data import ElasticSearchIterator


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Runs bindibot on test data.')
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
  parser.add_argument('--es_dest_hosts',
                      help='Store result data into elasticsearch.',
                      required=True, nargs='+')
  parser.add_argument('--es_dest_index',
                      help='Write result data into this index.',
                      required=True)
  parser.add_argument('--es_dest_type',
                      help='Write result data into this type.',
                      required=True)
  parser.add_argument('--query_function',
                      help='The query function to search for matches with.',
                      default='default_match_query')
  args = parser.parse_args()

  test_iterator = ElasticSearchIterator(
      [args.es_test_question_host], args.es_test_question_index,
      args.es_test_question_type)

  dest_es = Elasticsearch(args.es_dest_hosts)

  current_doc = test_iterator.next()
  while current_doc is not None:
    answer_pair = get_answers([args.es_question_host], args.es_question_index,
                              args.es_question_type, current_doc, 1,
                              query_functions[args.query_function])
    answer_doc = {
        'answer_id': answer_pair[0][0],
        'answer': answer_pair[0][1],
        'c_id': current_doc['c_id']
    }
    answer_doc['test_completed'] = False
    answer_doc['is_helpful'] = False
    answer_doc['query_function'] = args.query_function
    dest_es.index(args.es_dest_index, args.es_dest_type, body=answer_doc)
    current_doc = test_iterator.next()
