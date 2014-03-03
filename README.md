bindibot
========

A system that attempts to correctly answer piazza questions based on historical 
course data.

[Setup](#setup)

[Executables](#executables)

[Running](#running)

<a name="setup"></a>
Setup 
-----

First install requirements.txt (preferably in a
[virtualenv](https://pypi.python.org/pypi/virtualenv)).

    pip install -r requirements.txt

[Install](http://www.elasticsearch.org/) and run elasticsearch from inside the
elasticsearch directory.

    bin/elasticsearch

<a name="executables"></a>
Executables
-----------

Now, there are a few executables you can use:

`piazza_scanner.py`: Reads new bindibot scores from the last bindibot score
found and answers those questions.
Should be called in a cron job for deployment.

* `--username`: The username to login with.
* `--password`: The password for the username.
* `--course_id`: The id of the desired course.
* `--es_metadata_host`: Read last_id from elasticsearch.
* `--es_metadata_index`: Read last_id from this index.
* `--es_metadata_type`: Read last_id from this type.
* `--es_question_host`: Read question data from elasticsearch.
* `--es_question_index`: Read question data from this index.
* `--es_question_type`: Read question data from this type.

`piazza_api.py`: Allows getting data from a piazza course and writing to file,
elasticsearch, or printing to console.

* `--username`: The username to login with.
* `--password`: The password for the username.
* `--content_id`: The id of the desired content.
* `--course_id`: The id of the desired course.
* `--start_id`: The id to start writing the course data from.
* `--end_id`: The id to stop writing the course data at.
* `--data_file`: The file to output all course data when content_id is not 
provided.
* `--elasticsearch_host`: If provided will store raw data into elasticsearch.
* `--elasticsearch_index`: If provided will write data into this index.
* `--elasticsearch_type`: If provided will write data into this type.
* `--raw`: Print raw json data. Default is False.

`populate_cs225_data.py`: Uses the piazza_api to pull previous semester data
for cs225 and store in elasticsearch.

* `--username`: The username to login with.
* `--password`: The password for the username.
* `--elasticsearch_host`: Store raw data into elasticsearch.
* `--elasticsearch_index`: Write data into this index.
* `--elasticsearch_type`: Write data into this type.

`structure_question_data.py`: Converts raw piazza data from the piazza_api to
more structured data with question and answer information.

* `--es_source_host`: Read raw data from elasticsearch.
* `--es_source_index`: Read raw data from this index.
* `--es_source_type`: Read raw data from this type.
* `--es_dest_hosts`: Store structured data into elasticsearch.
* `--es_dest_index`: Write structured data into this index.
* `--es_dest_type`: Write structured data into this type.

`top_answers.py`: Given a query question returns the top relevant student and
instructor answers.

* `--question`: The input question that we want to answer.
* `--subject`: The input subject for the question we want to answer.
* `--es_hosts`: Read from this elasticsearch host.
* `--es_index`: Read data from this index.
* `--es_type`: Read data from this type.
* `--num_answers`: Number of answers that will be returned.

<a name="running"></a>
Running
-------

When running for the first time, one must populate the elastic search db with
course data.

1. `python populate_cs225_data.py`.
2. `python structure_question_data.py`.
3. `python piazza_scanner.py`.

Subsequent calls can just call `piazza_scanner.py`, no need to repopulate
elasticsearch.
