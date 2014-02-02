"""API to pull course question answer data from Piazza."""

import urllib2
import json
from cookielib import CookieJar


class AuthenticationError(Exception):
    """AuthenticationError"""


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
    print login_response
    if login_response['result'] != 'OK':
      raise AuthenticationError("Authentication failed.\n%s" % login_response['result'])

  def get_question_data(self, content_id, course_id):
    """Returns the data for the specified course_id and content_id.
       Returns None if the content type isn't a question."""
    content_url = 'https://piazza.com/logic/api?method=get.content'
    content_data = '{"method":"content.get","params":{"cid":"%s","nid":"%s"}}' % (content_id, course_id)
    content_response = json.loads(self.url_opener.open(content_url, content_data).read())
    if content_response['result']['type'] != 'question':
      return None
    content = {}
    content['question'] = content_response['result']['history'][0]['content']
    content['subject'] = content_response['result']['history'][0]['subject']
    for child in content_response['result']['children']:
      if child['type'] == 's_answer' and len(child['history']) > 0:
        content['student_answer'] = child['history'][0]['content']
      if child['type'] == 'i_answer' and len(child['history']) > 0:
        content['instructor_answer'] = child['history'][0]['content']
    return content


if __name__ == "__main__":
  piazza_api = PiazzaAPI('sivakum3@illinois.edu', 'piazza')
  print json.dumps(piazza_api.get_question_data(3016, 'h5oj0u0mpctyq'))