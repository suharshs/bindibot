"""
  Converts all raw data generated from populate_cs225_data.py into
  a more useful structure for bindibot.
  --es_source_host: Read raw data from elasticsearch.
  --es_source_index: Read raw data from this index.
  --es_source_type: Read raw data from this type.
  --es_dest_hosts: Store structured data into elasticsearch.
  --es_dest_index: Write structured data into this index.
  --es_dest_type: Write structured data into this type.
"""

import argparse
import elasticsearch


class ElasticSearchIterator:
  """Wrapper around elasticsearch scroll to get the next document."""

  def __init__(self, es_hosts, es_index, es_type,
               body='{"query": {"match_all": {}}}'):
    """Starts the iterator on the elasticsearch db."""
    self.es = elasticsearch.Elasticsearch(es_hosts)
    self.scroll_id = self.es.search(es_index, es_type, body, search_type='scan',
                                    scroll='10m', size=100)['_scroll_id']
    self.cache = []

  def next(self):
    """Returns the next document or None if we have reached the end."""
    if len(self.cache) == 0:
      scroll_results = self.es.scroll(self.scroll_id, scroll='10m')
      self.scroll_id = scroll_results['_scroll_id']
      self.cache = scroll_results['hits']['hits']
    if len(self.cache) > 0:
      return self.cache.pop()['_source']
    else:
      return None

def get_structured_doc(raw_doc):
  """Given a raw json object will return a structure json object."""
  structured_doc = {}
  structured_doc['question'] = raw_doc['result']['history'][0]['content']
  structured_doc['question_upvotes'] = len(raw_doc['result']['tag_good_arr'])
  structured_doc['subject'] = raw_doc['result']['history'][0]['subject']
  structured_doc['s_answer'] = ''
  structured_doc['s_answer_upvotes'] = 0
  structured_doc['i_answer'] = ''
  structured_doc['i_answer_upvotes'] = 0
  structured_doc['cid'] = raw_doc['result']['id']
  for child in raw_doc['result']['children']:
    if child['type'] == 's_answer' and len(child['history']) > 0:
      structured_doc['s_answer'] = child['history'][0]['content']
      structured_doc['s_answer_upvotes'] = len(child['tag_endorse'])
    if child['type'] == 'i_answer' and len(child['history']) > 0:
      structured_doc['i_answer'] = child['history'][0]['content'] 
      structured_doc['i_answer_upvotes'] = len(child['tag_endorse'])
  return structured_doc


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Structure raw json data.')
  parser.add_argument('--es_source_host',
                      help='Read raw data from elasticsearch.', required=True)
  parser.add_argument('--es_source_index',
                      help='Read raw data from this index.', required=True)
  parser.add_argument('--es_source_type',
                      help='Read raw data from this type.', required=True)
  parser.add_argument('--es_dest_hosts',
                      help='Store structured data into elasticsearch.',
                      required=True, nargs='+')
  parser.add_argument('--es_dest_index',
                      help='Write structured data into this index.',
                      required=True)
  parser.add_argument('--es_dest_type',
                      help='Write structured data into this type.',
                      required=True)
  args = parser.parse_args()

  source_iterator = ElasticSearchIterator(
      [args.es_source_host], args.es_source_index, args.es_source_type)
  dest_es = elasticsearch.Elasticsearch(args.es_dest_hosts)
  current_doc = source_iterator.next()
  while current_doc is not None:
    structured_doc = get_structured_doc(current_doc)
    if structured_doc['i_answer'] or structured_doc['s_answer']:
      dest_es.index(args.es_dest_index, args.es_dest_type, body=structured_doc)
    current_doc = source_iterator.next()
