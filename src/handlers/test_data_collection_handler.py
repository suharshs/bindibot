import sys
sys.path.append('./..')

from tornado.web import RequestHandler
from elasticsearch import Elasticsearch
from piazza_api import PiazzaAPI
from top_answers import get_answers
import random
from query_functions import query_functions


class TestDataCollectionHandler(RequestHandler):
  def get(self):
    question_doc, post_id = self.get_random_question_object()
    answers = get_answers(self.application.es_question_host,
                          self.application.es_question_index,
                          self.application.es_question_type,
                          question_doc, 10,
                          query_functions['tag_default_query'])
    self.render("test_data_collection.html",
                question=question_doc['question'],
                post_id=post_id,
                answers=answers)

  def post(self):
    form_data = self.request.arguments
    answers = form_data.get('answer', [])
    post_id = form_data['post-id'][0]

    dest_es = Elasticsearch(self.application.es_dest_hosts)

    # makes sure we count this post_id as seen.
    dest_es.index(self.application.es_dest_index,
                  self.application.es_dest_type,
                  body={'c_id': post_id, 'answer_id': '0'})
    for answer in answers:
      dest_es.index(self.application.es_dest_index,
                    self.application.es_dest_type,
                    body={'c_id': post_id, 'answer_id': answer})

    self.redirect('/')

  def get_random_question_object(self):
    """
    Gets a random question to populate the page with.
    """
    piazza = PiazzaAPI(self.application.username, self.application.password)
    post_id = random.choice(self.application.post_ids)
    question_doc = piazza.get_question_data(post_id, self.application.course_id)
    while 'error' in question_doc:
      post_id = random.choice(self.application.post_ids)
      question_doc = piazza.get_question_data(post_id,
          self.application.course_id)
    return (question_doc, post_id)
