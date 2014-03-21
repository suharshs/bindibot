import os
import logging
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options, define
from handlers.test_data_collection_handler import TestDataCollectionHandler


define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run tornado in debug mode", type=bool)
define('username', help='The username to login with.')
define('password', help='The password for the username.')
define('course_id', help='The id of the desired course.')
define('es_question_host', help='Read data from elasticsearch.')
define('es_question_index', help='Read data from this index.')
define('es_question_type', help='Read data from this type.')
define('es_dest_hosts', help='Store test data into elasticsearch.',
       multiple=True)
define('es_dest_index', help='Write test data into this index.')
define('es_dest_type', help='Write test data into this type.')

class Application(tornado.web.Application):
  def __init__(self):
    self.post_ids = range(2500, 3000)
    self.username = options.username
    self.password = options.password
    self.course_id = options.course_id
    self.es_question_host = options.es_question_host
    self.es_question_index = options.es_question_index
    self.es_question_type = options.es_question_type
    self.es_dest_hosts = options.es_dest_hosts
    self.es_dest_index = options.es_dest_index
    self.es_dest_type = options.es_dest_type

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
