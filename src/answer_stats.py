"""
Collects data on how well piazza_scanner answers questions.
--username: The username to login to piazza.
--password: The pasword for the username.
--bot_id: The id of the user that is the bot.
--start_id: The id to start collecting data from.
--course_id: the id of the piazza course.
"""

import argparse
import json
from piazza_api import PiazzaAPI


def get_answer_stats(username, password, bot_id, start_id, course_id):
  """
  Returns a dictionary with total answers, good answers, bad answers, and
  answers that have not been responded to.
  """
  piazza = PiazzaAPI(username, password)
  answer_stats = {}
  answer_stats['total'] = 0
  answer_stats['good'] = 0
  answer_stats['bad'] = 0
  answer_stats['good_and_bad'] = 0
  answer_stats['no_response'] = 0
  failed_reads = 0
  curr_id = start_id

  while failed_reads < 5:
    curr_id += 1
    question_doc = piazza.get_question_data(curr_id, course_id)
    if ('error' in question_doc and
        question_doc['error'] == 'Content_id out of range.'):
      failed_reads += 1
    elif 'error' not in question_doc:
      failed_reads = 0
      answer_type = get_answer_type(question_doc, bot_id)
      if 'no_answer' != answer_type:
        answer_stats['total'] += 1
        answer_stats[answer_type] += 1

  return answer_stats


def get_answer_type(question_doc, bot_id):
  """
  Given a question_doc returns the type of answer it was, good, bad,
  no_response, good_and_bad, or no_answer.
  """
  response = 'no_answer'
  for followup in question_doc['followups']:
    if followup['uid'] == bot_id:
      response = 'no_response'
      good = False
      bad = False
      for comment in followup['comments']:
        # &#43;1 is +1 after html encoding.
        if '&#43;1' in comment['content']:
          good = True
        if '-1' in comment['content']:
          bad = True
      if good and bad:
        response = 'good_and_bad'
      elif good:
        response = 'good'
      elif bad:
        response = 'bad'
      break
  return response


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Get Piazza question data.')
  parser.add_argument('--username', help='The username to login with.',
                      required=True)
  parser.add_argument('--password', help='The password for the username.',
                      required=True)
  parser.add_argument('--bot_id',
                      help='The id of the user that stats are be collected on.',
                      required=True)
  parser.add_argument('--start_id', help='The id to start reading data from.',
                      required=True, type=int)
  parser.add_argument('--course_id', help='The id of the desired course.',
                      required=True)
  args = parser.parse_args()

  answer_stats = get_answer_stats(args.username, args.password, args.bot_id,
                                  args.start_id, args.course_id)
  print json.dumps(answer_stats)
