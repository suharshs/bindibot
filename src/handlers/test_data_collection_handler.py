from tornado.web import RequestHandler
from elasticsearch import Elasticsearch


class TestDataCollectionHandler(RequestHandler):
  def get(self):
    question, answer, test_id = self.get_test_question_answer()
    self.render("test_data_collection.html",
                question=question,
                test_id=test_id,
                answer=answer)

  def post(self):
    form_data = self.request.arguments
    answer = form_data.get('answer', [])
    test_answer_id = form_data.get('test-id')

    test_answer_es = Elasticsearch([self.application.es_test_host])

    partial_doc = {'test_completed': True}
    if answer:
      partial_doc['is_helpful'] = True

    update_doc = {}
    update_doc['doc'] = partial_doc

    test_answer_es.update(index=self.application.es_test_index,
                          doc_type=self.application.es_test_type,
                          id=test_answer_id, body=update_doc, refresh=True)

    self.redirect('/')

  def generate_done_message(self):
    return ('No more questions', -1, '')

  def get_test_question_answer(self):
    """
    Gets a test answer to populate the page with.
    """
    query_string = """
    {
      "query": {
        "term" : {"test_completed": false}
      }
    }
    """
    answer_doc = None
    test_answer_es = Elasticsearch([self.application.es_test_host])
    search_results = test_answer_es.search(self.application.es_test_index,
                                           self.application.es_test_type,
                                           body=query_string, size=1)
    if search_results['hits']['total'] > 0:
      answer_doc = search_results['hits']['hits'][0]

    if not answer_doc:
      return self.generate_done_message()

    answer = answer_doc['_source']['answer']
    test_answer_id = answer_doc['_id']
    c_id = answer_doc['_source']['c_id']

    query_string = """
    {
      "query": {
        "term" : {"c_id": %s}
      }
    }
    """ % c_id
    test_question_es = Elasticsearch([self.application.es_test_question_host])
    search_results = test_question_es.search(
        self.application.es_test_question_index,
        self.application.es_test_question_type, body=query_string, size=1)
    question = search_results['hits']['hits'][0]['_source']['question']

    return (question, answer, test_answer_id)
