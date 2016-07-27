A simple quote displaying/querying app.

If there is a MONGOLAB_URI in the environment, it will be used as the database
to populate. Otherwise, the script will attempt to connect to the database
"quotefade_dev" on localhost on the default MongoDB port. This is the same
behavior as the app itself.

The app also uses the presence or absence of the MONGOLAB_URI in the
environment as a proxy for whether or not the app should be run in production
mode.