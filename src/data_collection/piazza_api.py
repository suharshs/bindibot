"""
  API to pull course question answer data from Piazza.
  Command line tool will retrieve content with the following flags specified.
  --username: The username to login with.
  --password: The password for the username.
  --content_id: The id of the desired content.
  --course_id: The id of the desired course.
"""

import argparse
from cookielib import CookieJar
import json
import os
import urllib2


class AuthenticationError(Exception):
    """Error in authenicating at login."""


class PiazzaAPI:
  """Provides access to the Piazza REST API."""

  def __init__(self, user, password):
    """Authenticates and instantiates the PiazzaAPI object."""
    self.cookie_jar = CookieJar()
    self.url_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_jar))
    self.authenticate(user, password)

  def authenticate(self, user, password):
    """Logs in the user and stores the session cookie."""
    login_url = 'https://piazza.com/logic/api?method=user.login'
    login_data = '{"method":"user.login","params":{"email":"%s","pass":"%s"}}' % (user, password)
    login_response = json.loads(self.url_opener.open(login_url, login_data).read())
    if login_response['result'] != 'OK':
      raise AuthenticationError("Authentication failed.\n%s" % login_response['result'])

  def get_question_data(self, content_id, course_id):
    """Returns the data for the specified course_id and content_id.
       Returns None if the content type isn't a question."""
    content_url = 'https://piazza.com/logic/api?method=get.content'
    content_data = '{"method":"content.get","params":{"cid":"%s","nid":"%s"}}' % (content_id, course_id)
    content_response = json.loads(self.url_opener.open(content_url, content_data).read())
    content = {}
    if not content_response['result']:
      content['error'] = 'Content_id out of range.'
    elif not 'type' in content_response['result'] or content_response['result']['type'] != 'question':
      content['error'] = 'Not a question.';
    elif not 'status' in content_response['result'] or content_response['result']['status'] == 'deleted':
      content['error'] = 'Content was deleted.'
    else:
      content['question'] = content_response['result']['history'][0]['content']
      content['subject'] = content_response['result']['history'][0]['subject']
      for child in content_response['result']['children']:
        if child['type'] == 's_answer' and len(child['history']) > 0:
          content['student_answer'] = child['history'][0]['content']
        if child['type'] == 'i_answer' and len(child['history']) > 0:
          content['instructor_answer'] = child['history'][0]['content']
    return content

  def write_course_question_data(self, course_id, output_file, start_id=1, end_id=4000):
    """Writes all question data from the specified course_id into output_file.
       One JSON object per line of the file."""
    content_id = start_id
    with open(output_file, 'a+') as f:
      while content_id < end_id:
        content = self.get_question_data(content_id, course_id)
        print content_id
        content_id += 1
        if not 'error' in content:
          f.write(json.dumps(content) + '\n')
      # Remove the extra newline char at the end of the file.
      f.seek(-1, os.SEEK_END)
      f.truncate()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Get Piazza question data.')
  parser.add_argument('--username', help='The username to login with.', required=True)
  parser.add_argument('--password', help='The password for the username.', required=True)
  parser.add_argument('--content_id', help='The id of the desired content. If not provided all course_ids data will be written to data_file.', default=None)
  parser.add_argument('--course_ids', help='The id of the desired course.', required=True, nargs='+')
  parser.add_argument('--start_id', help='The id to start writing the course data from.', type=int, default=1)
  parser.add_argument('--end_id', help='The id to stop writing the course data at.', type=int, default=4000)
  parser.add_argument('--data_file', help='The file to output all course data when content_id is not provided.', default=None)
  args = parser.parse_args()

  piazza_api = PiazzaAPI(args.username, args.password)
  if args.content_id:
    print json.dumps(piazza_api.get_question_data(args.content_id, args.course_ids[0]))
  elif args.data_file:
    for course_id in args.course_ids:
      piazza_api.write_course_question_data(course_id, args.data_file, start_id=args.start_id, end_id=args.end_id)
