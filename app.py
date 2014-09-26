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

@app.route('/')
def index():
  return flask.render_template('index.html')

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
    db.quotes.insert({'_id': idx, 'data': quote});
    return flask.jsonify({'status': 200})
  else:
    return 'Error', 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=debug)
