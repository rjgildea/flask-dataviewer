# Flask Dataviewer Application

Provides a Flask web service to extract the images from nexus files. 
It is based on dials to generate images. 
Need to use dials.python to get the correct environment.

gunicorn_runner allows the app to run on the command line but with worker threads.

## Install
Create virtualenv e.g. virtualenv .env
Install dependencies via pip install -r requirements.txt
Create a settings.cfg (see settings_sample.cfg)

Assumes you already have dials installed - pip does not install this for you

## Running
#!/usr/bin/env bash
source .env/bin/activate
export DATAVIEWER_SETTINGS=settings.cfg
module load dials
dials.python gunicorn_runner.py --workers x --host x.x.x.x --port xxxx )

Specify num workers 'x', host 'x.x.x.x' and port 'xxxx'
## Example 
dials.python gunicorn_runner.py --workers 3 --host 127.0.0.1 --port 5000



