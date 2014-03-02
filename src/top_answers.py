"""
Given a question, prints the top answers that most likely answer the question.
--question: The input question that we want to answer.
--subject: The input subject for the question we want to answer.
--es_hosts: Read from this elasticsearch host.
--es_index: Read data from this index.
--es_type: Read data from this type.
--num_answers: Number of answers that will be returned.
"""

import argparse
import elasticsearch
from query_functions import default_match_query

def get_similar_question_objects(es_hosts, es_index, es_type, in_question_doc,
                                 num_answers,
                                 query_function):
  """
  Returns the similar question objects to the in_question.
  """
  es = elasticsearch.Elasticsearch(es_hosts)
  query_string = query_function(in_question_doc)
  search_results = es.search(es_index, es_type, body=query_string,
                             size=num_answers)
  return search_results['hits']['hits']

def get_answers(es_hosts, es_index, es_type, question_doc, num_answers,
                query_function):
  """
  Returns the top num_answers for the input question.
  Returns a dictionary with s_answers and i_answers.
  """
  question_docs = get_similar_question_objects(es_hosts, es_index, es_type,
                                               question_doc, num_answers,
                                               query_function)
  s_answers = [doc['_source']['s_answer'] for doc in question_docs
               if doc['_source']['s_answer']]
  i_answers = [doc['_source']['i_answer'] for doc in question_docs
               if doc['_source']['i_answer']]
  return {'s_answers': s_answers, 'i_answers': i_answers}

def print_answers(answers):
  """
  Prints the top answers to the console given an answers dictionary
  from get_answers.
  """
  print 'Student Answers:'
  for s_answer in answers['s_answers']:
    print s_answer + '\n'
  print '--------------------------------------------------------------\n'
  print 'Instructor Answers:'
  for i_answer in answers['i_answers']:
    print i_answer + '\n'


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
      description='Given a query question, returns the top relevant answers')
  parser.add_argument('--question',
                      help='The input question that we want to answer.',
                      required=True)
  parser.add_argument('--subject',
                      help='The subject for the question we want to answer.',
                      required=None)
  parser.add_argument('--es_hosts', help='Read from this elasticsearch host.',
                      required=True, nargs='+')
  parser.add_argument('--es_index', help='Read data from this index.',
                      required=True)
  parser.add_argument('--es_type', help='Read data from this type.',
                      required=True)
  parser.add_argument('--num_answers',
                      help='Number of answers that will be returned', type=int,
                      default=5)
  args = parser.parse_args()

  question_doc = {}
  question_doc['question'] = args.question
  question_doc['subject'] = args.subject
  answers = get_answers(args.es_hosts, args.es_index, args.es_type,
                        question_doc, args.num_answers, default_match_query)
  print_answers(answers)
