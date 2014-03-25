"""
Populates the test data questions for bindibot_stats into elasticsearch.
"""

import argparse
from elasticsearch import Elasticsearch
from piazza_api import PiazzaAPI


unique_question_ids_query = """
{
 "query" : { "query_string" : {"query" : "*","fields":["c_id"]} },
 "facets" : {
   "unique_questions" : { "terms" : {"fields" : ["c_id"],"order":"term","size":100} }
 }
}
"""

class UniqueQuestionsIterator:
  """
  Wrapper around elasticsearch scroll to get the next document facet.
  """

  def __init__(self, es_hosts, es_index, es_type,
               body=unique_question_ids_query):
    """Starts the iterator on the elasticsearch db."""
    self.es = Elasticsearch(es_hosts)
    self.scroll_id = self.es.search(es_index, es_type, body, search_type='scan',
                                    scroll='10m', size=100)['_scroll_id']
    self.cache = []

  def next(self):
    """Returns the next document or None if we have reached the end."""
    if len(self.cache) == 0:
      scroll_results = self.es.scroll(self.scroll_id, scroll='10m')
      self.scroll_id = scroll_results['_scroll_id']
      if 'facets' in scroll_results:
        self.cache = scroll_results['facets']['unique_questions']['terms']
    if len(self.cache) > 0:
      return int(self.cache.pop()['term'])
    else:
      return None


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Collects data for testing.')
  parser.add_argument('--username', help='The username to login with.',
                      required=True)
  parser.add_argument('--password', help='The password for the username.',
                      required=True)
  parser.add_argument('--course_id', help='The id of the desired course.',
                      required=True)
  parser.add_argument('--es_test_host',
                      help='Read data from elasticsearch.',
                      required=True)
  parser.add_argument('--es_test_index',
                      help='Read data from this index.',
                      required=True)
  parser.add_argument('--es_test_type',
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
  args = parser.parse_args()

  piazza = PiazzaAPI(args.username, args.password)

  dest_es = Elasticsearch(args.es_dest_hosts)

  test_iterator = UniqueQuestionsIterator(
      [args.es_test_host], args.es_test_index, args.es_test_type)

  current_id = test_iterator.next()
  while current_id is not None:
    question_doc = piazza.get_question_data(current_id, args.course_id)
    question_doc['c_id'] = current_id
    dest_es.index(args.es_dest_index, args.es_dest_type,
                  body=question_doc)
    current_id = test_iterator.next()

