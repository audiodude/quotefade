import os
import sys

import pymongo

MONGO_URI = os.environ.get('MONGOLAB_URI')
if MONGO_URI:
  client = pymongo.MongoClient(MONGO_URI)
  db = client.get_default_database()
else:
  client = pymongo.MongoClient()
  db = client.quotefade_dev


def init_db(quote):
  idx = 0
  existing = db.quotes.find_one({'_id': {'$gte': idx}})
  if existing:
    msg = 'The database already contains a quote: %r' % existing['data']
    raise ValueError(msg)
    
  db.quotes.insert({'_id': idx, 'data': quote})
  
  ops = db.ops.find_one({'count': {'$exists': True}})
  if ops:
    db.ops.update({'count': {'$exists': True}}, {
        '$inc': {'count': len(quote)}
    })
  else:
    db.ops.insert({'count': len(quote)})


if __name__ == '__main__':
  try:
    quote = sys.argv[1]
  except IndexError:
    print('The first argument to the script should be the quote to init the '
          'db with')
    sys.exit(1)

  init_db(quote)
