import os
import time
import logging

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt_simple import jwt_required

import h5py
from db import get_dc


api_bp = Blueprint('nexus', __name__)
api = Api(api_bp)

h5exts = ['h5', 'nxs']


class NexusScanScalars(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dcid', type=int, required=True, help='No data collection id specified')
        self.reqparse.add_argument('entry', type=int, help='H5 entry')

        super(NexusScanScalars, self).__init__()

    @jwt_required
    def get(self):
        args = self.reqparse.parse_args()

        dc = get_dc(args.dcid)
        if dc is None:
            logging.getLogger('image-service').error('No such data collection {}'.format(args.dcid))
            abort(400, message='No such data collection')

        ext = os.path.splitext(str(dc['file_template_full_python']))[1][1:].strip().lower()
        if not ext in h5exts:
            raise AttributeError('File for this scan is not nexus')

        root = dc['imgContainerSubPath']
        scalars = []
        with h5py.File(dc['file_template_full_python'], mode='r') as h5:
            print('entry', args.entry)
            if args.entry is not None:
                entries = [m for m in h5]
                path = root.split('/')
                root = '{entry}/{path}'.format(entry=entries[args.entry], path='/'.join(path[1:]))

            for group_name in h5[root]:
                group = h5['{root}/{group}'.format(root=root, group=group_name)]
                if len(group.shape) == 1:
                    scalars.append({
                        'title': group_name,
                        'data': group[()].tolist()
                    })

        return scalars


class NexusScanSpectra(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('dcid', type=int, required=True, help='No data collection id specified')
        self.reqparse.add_argument('point', type=int, required=True, help='No data collection point specified')

        super(NexusScanSpectra, self).__init__()

    @jwt_required
    def get(self):
        args = self.reqparse.parse_args()

        dc = get_dc(args.dcid)
        if dc is None:
            logging.getLogger('image-service').error('No such data collection {}'.format(args.dcid))
            abort(400, message='No such data collection')

        ext = os.path.splitext(str(dc['file_template_full_python']))[1][1:].strip().lower()
        if not ext in h5exts:
            raise AttributeError('File for this scan is not nexus')

        root = dc['imgContainerSubPath']
        print('NexusScanSpectra', root)
        spectra = []
        with h5py.File(dc['file_template_full_python'], mode='r') as h5:
            for group_name in h5[root]:
                group = h5['{root}/{group}'.format(root=root, group=group_name)]
                if len(group.shape) == 2:
                    if args.point < len(group):
                        spectra.append({
                            'title': group_name,
                            'shape': group.shape,
                            'data': group[args.point].tolist()
                        })

        return spectra


api.add_resource(NexusScanScalars, '/nexus/scalars')
api.add_resource(NexusScanSpectra, '/nexus/spectra')
