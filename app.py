import binascii
import datetime
import os

import flask
import pymongo

app = flask.Flask(__name__)

MONGO_URI = os.environ.get('MONGOLAB_URI')
if MONGO_URI:
  client = pymongo.MongoClient(MONGO_URI)
  db = client.get_default_database()
  debug = False
else:
  client = pymongo.MongoClient()
  db = client.quotefade_dev
  debug = True

QUOTE_DISPLAY_MULTIPLIER = 34

def find_available_index(max_id):
  while True:
    orig_max_id = max_id
    for quote in db.quotes.find({'_id': {'$gte': max_id}}):
      if quote['_id'] > max_id:
        max_id = quote['_id']
    if max_id == orig_max_id:
      return max_id + 1

@app.route('/')
def index():
  ops = db.ops.find_one({})
  token = binascii.b2a_hex(os.urandom(16))
  # TODO: cleanup these timestamps as a cron job.
  db.timestamps.insert({
      'timestamp': datetime.datetime.now(),
      'token': token,
      'count': ops['count'],
  })
  return flask.render_template('index.html', token=token)

@app.route('/get_quotes')
def get_quotes():
  start = int(flask.request.args.get('start', 0))
  count = int(flask.request.args.get('count', 25))

  if start < 0:
    start = 0

  if count > 100:
    count = 100

  return flask.jsonify(
    quotes=list(db.quotes.find({
      '_id': {'$gte': start, '$lte': start + count}
    })))

@app.route('/add_quote', methods=['POST'])
def add_quote():
  quote = flask.request.form['quote'][:256]
  idx = int(flask.request.form['last_idx'])

  token_data = db.timestamps.find_one({'token': flask.request.form['token']})
  seconds_delta = datetime.timedelta(
    seconds=token_data['count'] * QUOTE_DISPLAY_MULTIPLIER / 1000)
  expected_time = (token_data['timestamp'] + seconds_delta)
  if expected_time >= datetime.datetime.now():
    # This is only if someone is trying to forge/bypass a token.
    return 'Error', 400

  existing = db.quotes.find_one({'_id': {'$gte': idx}})
  if existing:
    idx = find_available_index(idx)

  if quote:
    retries = 5
    while retries > 0:
      try:
        db.quotes.insert({'_id': idx, 'data': quote});
        break
      except pymongo.errors.DuplicateKeyError:
        idx = find_available_index(idx)
        retries -= 1
    else:
      # Else is executed if while didn't break, so we never inserted the quote.
      return flask.jsonify({
          'error': 'Wow we\'re busy! Your quote could not be inserted. Feel '
                   'free to try again.',
          'last_idx': idx,
      })

    db.ops.update({'count': {'$exists': True}}, {
        '$inc': {'count': len(quote)}
    })
    return flask.jsonify({'error': None})

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=debug)
