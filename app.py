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

from flask import Flask
from flask_jwt_simple import JWTManager

from api.diffractionimage import api_bp as di_api


def create_app():
    app = Flask(__name__)
    app.config.from_envvar('DATAVIEWER_SETTINGS')
    app.register_blueprint(di_api)

    jwt = JWTManager(app)

    return app
