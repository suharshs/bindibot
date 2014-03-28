import os
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options, define
from handlers.test_data_collection_handler import TestDataCollectionHandler


define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run tornado in debug mode", type=bool)

class Application(tornado.web.Application):
  def __init__(self):
    self.es_test_question_host = 'chara.cs.illinois.edu:9200'
    self.es_test_question_index = 'cs225'
    self.es_test_question_type = 'test_questions'
    self.es_test_host = 'chara.cs.illinois.edu:9200'
    self.es_test_index = 'cs225'
    self.es_test_type = 'test_answers'

    handlers = [
        tornado.web.URLSpec(r'/', TestDataCollectionHandler)
    ]

    current_dir = os.path.dirname(__file__)

    settings = dict(
        template_path=os.path.join(current_dir, 'templates'),
        static_path=os.path.join(current_dir, 'static'),
        debug=options.debug,
        autoescape='xhtml_escape',
        cookie_secret='addcookiesecrethere',
        xsrf_cookies=True
    )

    super(Application, self).__init__(handlers, **settings)

    logging.info('Server started on port {0}'.format(options.port))


if __name__ == "__main__":
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()
