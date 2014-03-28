"""
Runs bindibot versions on fixed test data and outputs results.
"""

import argparse
from elasticsearch import Elasticsearch


num_correct_query = """
{
  "query" : { "query_string" : {"query" : "*","fields":["is_helpful"]} },
  "facets" : {
  "num_questions" : {
    "terms" : {"fields" : ["is_helpful"],"order":"term","size":100} }
 }
}
"""


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Collects stats on bindibot.')
  parser.add_argument('--es_test_host',
                      help='Read test data from elasticsearch.', required=True)
  parser.add_argument('--es_test_index',
                      help='Read test data from this index.', required=True)
  parser.add_argument('--es_test_type',
                      help='Read test data from this type.', required=True)
  args = parser.parse_args()

  test_es = Elasticsearch([args.es_test_host])
  search_results = test_es.search(args.es_test_index, args.es_test_type,
                                  num_correct_query)
  answer_counts = search_results['facets']['num_questions']['terms']
  num_correct = 0
  for count in answer_counts:
    if count['term'] == 'T':
      num_correct = count['count']

  print '%s percent correct on the test data.' % num_correct

