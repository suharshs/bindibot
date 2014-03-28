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
from copy import deepcopy
from elasticsearch import Elasticsearch
import course_data
from util import ElasticsearchIterator


def get_structured_docs(raw_doc):
  """
  Given a raw json object will return a list of structured json objects.
  One for each type of answer.
  """
  docs = []
  structured_doc = {}
  structured_doc['question'] = raw_doc['result']['history'][0]['content']
  structured_doc['question_upvotes'] = len(raw_doc['result']['tag_good_arr'])
  structured_doc['subject'] = raw_doc['result']['history'][0]['subject']
  structured_doc['answer'] = ''
  structured_doc['cid'] = raw_doc['result']['id']
  tag_map = course_data.tag_maps[raw_doc.get('course_name', 'default')]
  for i in range(len(raw_doc['result']['tags'])):
    if raw_doc['result']['tags'][i] in tag_map:
      raw_doc['result']['tags'][i] = tag_map[raw_doc['result']['tags'][i]]
  structured_doc['tags'] = ' '.join(raw_doc['result']['tags'])
  structured_doc['followups'] = []
  for child in raw_doc['result']['children']:
    if child['type'] == 'followup':
      followup_doc = {}
      followup_doc['uid'] = child.get('uid', 'ANON')
      followup_doc['content'] = child['subject']
      followup_doc['comments'] = []
      for comment in child['children']:
        followup_doc['comments'].append({
          'uid': comment.get('uid', 'ANON'),
          'content': comment['subject']
        })
      structured_doc['followups'].append(followup_doc)
  for child in raw_doc['result']['children']:
    if ((child['type'] == 's_answer' or child['type'] == 'i_answer')
        and len(child['history']) > 0):
      structured_doc['answer'] = child['history'][0]['content']
      structured_doc['answer_upvotes'] = len(child['tag_endorse'])
      structured_doc['type'] = child['type']
      structured_doc['i_endorsed'] = False
      for endorsement in child['tag_endorse']:
        if endorsement['admin']:
          structured_doc['i_endorsed'] = True
      docs.append(deepcopy(structured_doc))
  return docs


if __name__ == '__main__':
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

  source_iterator = ElasticsearchIterator(
      [args.es_source_host], args.es_source_index, args.es_source_type)
  dest_es = Elasticsearch(args.es_dest_hosts)
  current_doc = source_iterator.next()
  while current_doc is not None:
    structured_docs = get_structured_docs(current_doc)
    for structured_doc in structured_docs:
      if structured_doc['answer']:
        dest_es.index(args.es_dest_index, args.es_dest_type,
                      body=structured_doc)
    current_doc = source_iterator.next()
