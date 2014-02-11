"""
  Sanitize data strings to get ready for scoring.
  Command line tool will clean the json strings and ooutput a new file with the clean strings.
  --input_file: The name of the file with the raw data from piazza_api.
  --output_file: The name of the file where the cleaned data should be written.
"""

import argparse
import json


def clean_data(input_filename, output_filename):
  """Cleans the raw data returned from piazza_api."""
  with open(input_filename, 'r') as input_file:
    with open(output_filename, 'a+') as output_file:
      for content_string in input_file.readlines():
        content_json = json.loads(content_string)
        content_json['student_answer'] = clean_string(content_json.get('student_answer', ''))
        content_json['instructor_answer'] = clean_string(content_json.get('instructor_answer', ''))
        content_json['question'] = clean_string(content_json.get('question', ''))
        content_json['subject'] = clean_string(content_json.get('question', ''))
        if content_json['question'] and (content_json['student_answer'] or content_json['instructor_answer']):
          output_file.write(json.dumps(content_json) + '\n')

def clean_string(input_string):
  """Cleans an input string by removing case and whitespace."""
  return ' '.join([word.strip() for word in input_string.lower().splitlines()])


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Sanitize Piazza question data.')
  parser.add_argument('--input_file', help='The name of the file with the raw data from piazza_api.', required=True)
  parser.add_argument('--output_file', help='The name of the file where the cleaned data should be written.', required=True)
  args = parser.parse_args()

  clean_data(args.input_file, args.output_file)
