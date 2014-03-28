"""
Populates the test data questions for bindibot_stats into elasticsearch.
"""

import argparse
from elasticsearch import Elasticsearch
from piazza_api import PiazzaAPI
from random import shuffle


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Collects data for testing.')
  parser.add_argument('--username', help='The username to login with.',
                      required=True)
  parser.add_argument('--password', help='The password for the username.',
                      required=True)
  parser.add_argument('--course_id', help='The id of the desired course.',
                      required=True)
  parser.add_argument('--es_dest_hosts',
                      help='Store test data into elasticsearch.',
                      required=True, nargs='+')
  parser.add_argument('--es_dest_index',
                      help='Write test data into this index.',
                      required=True)
  parser.add_argument('--es_dest_type',
                      help='Write test data into this type.',
                      required=True)
  args = parser.parse_args()

  piazza = PiazzaAPI(args.username, args.password)

  dest_es = Elasticsearch(args.es_dest_hosts)

  c_ids = range(1,3000)
  shuffle(c_ids)

  current_id = c_ids.pop()
  completed = 0
  while completed < 100:
    question_doc = piazza.get_question_data(current_id, args.course_id)
    while 'error' in question_doc:
      current_id = c_ids.pop()
      question_doc = piazza.get_question_data(current_id, args.course_id)
    question_doc['c_id'] = current_id
    dest_es.index(args.es_dest_index, args.es_dest_type,
                  body=question_doc)
    completed += 1
    current_id = c_ids.pop()

