"""
Populates the test data and store in elasticsearch to verify different versions
of bindibot.
next_id: 2539
"""

import argparse
from elasticsearch import Elasticsearch
from piazza_api import PiazzaAPI
from top_answers import get_answers
from query_functions import query_functions


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Collects data for testing.')
  parser.add_argument('--username', help='The username to login with.',
                      required=True)
  parser.add_argument('--password', help='The password for the username.',
                      required=True)
  parser.add_argument('--course_id', help='The id of the desired course.',
                      required=True)
  parser.add_argument('--es_question_host',
                      help='Read data from elasticsearch.',
                      required=True)
  parser.add_argument('--es_question_index',
                      help='Read data from this index.',
                      required=True)
  parser.add_argument('--es_question_type',
                      help='Read data from this type.',
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
  parser.add_argument('--start_id',
                      help='The id to start collecting accurate data.',
                      required=True, type=int)
  args = parser.parse_args()

  piazza = PiazzaAPI(args.username, args.password)

  curr_id = args.start_id

  dest_es = Elasticsearch(args.es_dest_hosts)

  while True:
    question_doc = piazza.get_question_data(curr_id, args.course_id)
    if 'error' not in question_doc:
      answers = get_answers(args.es_question_host, args.es_question_index,
                            args.es_question_type, question_doc, 10,
                            query_functions['default_match_query'])
      for answer in answers:
        print curr_id
        print question_doc['question']
        print '\n\n'
        print answer[1]
        print '\n\n'
        print 'Did the response help answer the question? (y/n/s)'
        reply = raw_input('-> ')
        if reply == 's':
          break
        helpful = (reply == 'y')
        doc = {'cid': curr_id, 'answer': answer[1], 'helpful': helpful}
        dest_es.index(args.es_dest_index, args.es_dest_type, body=doc)
    curr_id += 1

