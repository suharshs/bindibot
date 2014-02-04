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
      content['error'] = 'Content_id out of range'
    elif content_response['result']['type'] != 'question':
      content['error'] = 'Not a question.';
    else:
      content['question'] = content_response['result']['history'][0]['content']
      content['subject'] = content_response['result']['history'][0]['subject']
      for child in content_response['result']['children']:
        if child['type'] == 's_answer' and len(child['history']) > 0:
          content['student_answer'] = child['history'][0]['content']
        if child['type'] == 'i_answer' and len(child['history']) > 0:
          content['instructor_answer'] = child['history'][0]['content']
    return content

  def write_course_question_data(self, course_id, output_file):
    pass



if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Get Piazza question data.')
  parser.add_argument('--username', help='The username to login with.', required=True)
  parser.add_argument('--password', help='The password for the username.', required=True)
  parser.add_argument('--content_id', help='The id of the desired content.', required=True)
  parser.add_argument('--course_id', help='The id of the desired course.', required=True)
  args = parser.parse_args()

  piazza_api = PiazzaAPI(args.username, args.password)
  print json.dumps(piazza_api.get_question_data(args.content_id, args.course_id))
