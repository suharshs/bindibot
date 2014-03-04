"""
Reads new bindibot scores from the last bindibot score found and answers those
questions. Should be called in a cron job from deployment.
--username: The username to login with.
--password: The password for the username.
--course_id: The id of the desired course.
--es_metadata_host: Read last_id from elasticsearch.
--es_metadata_index: Read last_id from this index.
--es_metadata_type: Read last_id from this type.
--es_question_host: Read question data from elasticsearch.
--es_question_index: Read question data from this index.
--es_question_type: Read question data from this type.
--query_function: The query function to search for matches with.
"""

import argparse
from elasticsearch import Elasticsearch
from piazza_api import PiazzaAPI
from top_answers import get_answers
from query_functions import query_functions


class PiazzaScanner:
  """
  Scans piazza and answers unanswered questions. Should be run in cron.
  """
  def __init__(self, username, password, course_id, es_metadata_host,
               es_metadata_index, es_metadata_type, es_question_host,
               es_question_index, es_question_type, query_function):
    self.piazza = PiazzaAPI(username, password)
    self.course_id = course_id
    self.es_metadata = Elasticsearch(es_metadata_host)
    self.es_metadata_index = es_metadata_index
    self.es_metadata_type = es_metadata_type
    self.es_question_host = es_question_host
    self.es_question_index = es_question_index
    self.es_question_type = es_question_type
    self.query_function = query_function

  def run(self):
    """
    Runs the Scanner from the last_id, answering all new questions in a
    followup post.
    """
    self.answer_questions(self.get_new_questions())

  def answer_questions(self, questions):
    """
    Answers questions given a list of question objects.
    """
    for question in questions:
      answers = get_answers(self.es_question_host, self.es_question_index,
                            self.es_question_type, question, 10,
                            self.query_function)
      response = self.generate_response_string(answers)
      if response:
        self.piazza.post_followup(self.course_id, response, cid=question['cid'])

  def generate_response_string(self, answers):
    """
    Generates a response string message with the answers object.
    """
    response = ''
    if len(answers['i_answers']) > 0:
      response += 'TOP INSTRUCTOR ANSWER: '
      response += answers['i_answers'][0]
    if response:
      response += '<p>\n</p>'
    if len(answers['s_answers']) > 0:
      response += 'TOP STUDENT ANSWER: '
      response += answers['s_answers'][0] 
    if response:
      response += ('<p>\n</p>--This is an autogenerated message. If it\'s' +
                   ' helpful please comment a \'+1\'. Otherwise comment a ' +
                   ' \'-1\'. Thank you. <3.')
    return response

  def get_new_questions(self):
    """
    Returns list of all unanswered question objects from last_id.
    """
    last_id = self.get_last_id()
    failed_reads = 0
    curr_id = last_id
    new_questions = []

    while failed_reads < 5:
      curr_id += 1
      new_data = self.piazza.get_question_data(curr_id, self.course_id)
      if ('error' in new_data and
          new_data['error'] == 'Content_id out of range.'):
        failed_reads += 1
      elif 'error' not in new_data:
        failed_reads = 0
        last_id = curr_id
        new_questions.append(new_data)

    self.write_last_id(last_id)
    return new_questions

  def get_last_id(self):
    """
    Reads the last_id from the elasticsearch store.
    """
    return self.es_metadata.get(index=self.es_metadata_index,
                                doc_type=self.es_metadata_type,
                                id=1)['_source']['last_read']

  def write_last_id(self, last_id):
    """
    Writes the new value of last_id to elasticsearch store.
    """
    self.es_metadata.update(index=self.es_metadata_index,
                            doc_type=self.es_metadata_type, id=1,
                            body='{"doc":{"last_read": %s}}' % last_id)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Scanner of new piazza data.')
  parser.add_argument('--username', help='The username to login with.',
                      required=True)
  parser.add_argument('--password', help='The password for the username.',
                      required=True)
  parser.add_argument('--course_id', help='The id of the desired course.',
                      required=True)
  parser.add_argument('--es_metadata_host',
                      help='Read last_id from elasticsearch.',
                      required=True)
  parser.add_argument('--es_metadata_index',
                      help='Read last_id from this index.',
                      required=True)
  parser.add_argument('--es_metadata_type',
                      help='Read last_id from this type.',
                      required=True)
  parser.add_argument('--es_question_host',
                      help='Read question data from elasticsearch.',
                      required=True)
  parser.add_argument('--es_question_index',
                      help='Read question data from this index.',
                      required=True)
  parser.add_argument('--es_question_type',
                      help='Read question data from this type.',
                      required=True)
  parser.add_argument('--query_function',
                      help='The query function to search for matches with.',
                      default='default_match_query')
  args = parser.parse_args()

  scanner = PiazzaScanner(args.username, args.password, args.course_id,
                          args.es_metadata_host, args.es_metadata_index,
                          args.es_metadata_type, args.es_question_host,
                          args.es_question_index, args.es_question_type,
                          query_functions[args.query_function])
  scanner.run()
