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

  existing = db.quotes.find_one({'_id': {'$gte': idx}})
  if not existing:
    token_data = db.timestamps.find_one({'token': flask.request.form['token']})
    seconds_delta = datetime.timedelta(
      seconds=token_data['count'] * QUOTE_DISPLAY_MULTIPLIER / 1000)
    expected_time = (token_data['timestamp'] + seconds_delta)
    if expected_time < datetime.datetime.now():
      # Expected time is before now, so enough time has passed
      db.quotes.insert({'_id': idx, 'data': quote});
      db.ops.update({'count': {'$exists': True}}, {
          '$inc': {'count': len(quote)}
      })
      return flask.jsonify({'status': 200})
    else:
      return 'Error', 400
  else:
    return 'Error', 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=debug)
