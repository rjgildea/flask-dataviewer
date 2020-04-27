#!/usr/bin/env python
#
#   Restful service to generate:
#       Diffraction images from hdf5 / cbf files
#       Maps from mtz files
#
#   This requires
#       * flask
#       * flast_restful
#       * flask_jwt_simple

# module load dials
# libtbx.pip install --user flask flast_restful flask_jwt_simple

import logging
import logging.handlers

from flask import Flask
from flask_jwt_simple import JWTManager

from api.diffractionimage import api_bp as di_api
from api.nexus import api_bp as nexus_api

logger = logging.getLogger('image-service')
handler = logging.handlers.RotatingFileHandler('logs/image-service.log', maxBytes=1000000, backupCount=5)
handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(message)s]"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('DATAVIEWER_SETTINGS')
    app.register_blueprint(di_api)
    app.register_blueprint(nexus_api)

    jwt = JWTManager(app)

    return app
