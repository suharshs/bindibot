"""
Runs bindibot on the chosen test questions.
"""

import argparse
from elasticsearch import Elasticsearch
from top_answers import get_answers
from query_functions import query_functions
from util import ElasticsearchIterator


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Runs bindibot on test data.')
  parser.add_argument('--es_test_question_host',
                      help='Read test questions from elasticsearch.',
                      default='chara.cs.illinois.edu:9200')
  parser.add_argument('--es_test_question_index',
                      help='Read test questions from this index.',
                      default='cs225')
  parser.add_argument('--es_test_question_type',
                      help='Read test questions from this type.',
                      default='test_questions')
  parser.add_argument('--es_question_host',
                      help='Read question data from elasticsearch.',
                      default='chara.cs.illinois.edu:9200')
  parser.add_argument('--es_question_index',
                      help='Read question data from this index.',
                      default='cs225')
  parser.add_argument('--es_question_type',
                      help='Read question data from this type.',
                      default='structured')
  parser.add_argument('--es_dest_host',
                      help='Store result data into elasticsearch.',
                      default='chara.cs.illinois.edu:9200')
  parser.add_argument('--es_dest_index',
                      help='Write result data into this index.',
                      default='cs225')
  parser.add_argument('--es_dest_type',
                      help='Write result data into this type.',
                      default='test_answers')
  parser.add_argument('--query_function',
                      help='The query function to search for matches with.',
                      required=True)
  args = parser.parse_args()

  test_iterator = ElasticsearchIterator(
      [args.es_test_question_host], args.es_test_question_index,
      args.es_test_question_type)

  dest_es = Elasticsearch([args.es_dest_host])

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

    # check if the question answer pair has already been completed by a
    # previous version.
    query_string = """
    {
      "query": {
        "bool": {
          "must": [
            {
              "query_string": {
                "default_field": "test_answers.answer_id",
                "query": "%s"
              }
            },
            {
              "term": {
                "test_answers.c_id": "%s"
              }
            }
          ]
        }
      }
    }
    """ % (answer_doc['answer_id'], answer_doc['c_id'])

    search_results = dest_es.search(args.es_dest_index, args.es_dest_type,
                                    body=query_string)

    answer_doc['test_completed'] = False
    answer_doc['is_helpful'] = False
    answer_doc['query_function'] = args.query_function

    if search_results['hits']['total'] > 0:
      answer_doc['test_completed'] = True
      is_helpful = search_results['hits']['hits'][0]['_source']['is_helpful']
      answer_doc['is_helpful'] = is_helpful

    dest_es.index(args.es_dest_index, args.es_dest_type, body=answer_doc)
    current_doc = test_iterator.next()
