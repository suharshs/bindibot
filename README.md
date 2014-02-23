bindibot
========

A system that attempts to correctly answer piazza questions based on historical course data.

Setup
-----

First install requirements.txt (preferably in a [virtualenv](https://pypi.python.org/pypi/virtualenv)).

    pip install -r requirements.txt

[Install](http://www.elasticsearch.org/) and run elasticsearch from inside the elasticsearch directory.

    bin/elasticsearch

Now there are a few executables you can use:

piazza_api.py

popuylate_cs225_data.py

structure_question_data.py

top_answers.py
