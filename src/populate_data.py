"""
Gets all cs225 previous semester data and populate elasticsearch index.
--username: The username to login with.
--password: The password for the username.
--elasticsearch_host: Store raw data into elasticsearch.
--elasticsearch_index: Write data into this index.
--elasticsearch_type: Write data into this type.
"""

import argparse
from piazza_api import PiazzaAPI

from course_data import courses


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Get Piazza question data.')
  parser.add_argument('--username', help='The username to login with.',
                      required=True)
  parser.add_argument('--password', help='The password for the username.',
                      required=True)
  parser.add_argument('--elasticsearch_hosts',
                      help='Store raw data into elasticsearch.', required=True,
                      nargs='+')
  parser.add_argument('--elasticsearch_index',
                      help='Store raw data into this elasticsearch index.',
                      required=True)
  parser.add_argument('--elasticsearch_type',
                      help='Store raw data into this elasticsearch type.',
                      required=True)
  args = parser.parse_args()

  course = courses['cs225']

  piazza_api = PiazzaAPI(args.username, args.password)
  for course in courses:
    piazza_api.write_course_data_elasticsearch(
        es_hosts=args.elasticsearch_hosts, es_index=args.elasticsearch_index,
        es_type=args.elasticsearch_type, course_id=course['course_id'],
        start_id=1, end_id=course['max_id'], course_name=course['name'])
