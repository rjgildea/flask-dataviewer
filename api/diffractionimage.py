import os
import time
import logging

from PIL import Image
import PIL.ImageOps

from flask import Blueprint, request, after_this_request, send_file
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt_simple import jwt_required

from dxtbx.datablock import DataBlockFactory
from dials.command_line.export_bitmaps import imageset_as_bitmaps
from dials.command_line.export_bitmaps import phil_scope

from db import get_filepath_from_dc


api_bp = Blueprint('diffractionimage', __name__)
api = Api(api_bp)


class DataCollectionImage(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('image', type=int, required=True, help='No image number specified')
        self.reqparse.add_argument('dcid', type=int, required=True, help='No data collection id specified')
        self.reqparse.add_argument('binning', type=int, help='Binning must be a number')
        self.reqparse.add_argument('quality', type=int, help='Quality must be a number between 1 and 100')
        self.reqparse.add_argument('threshold', type=int, help='Enable thresholding, must be 1 or 0')

        super(DataCollectionImage, self).__init__()


    @jwt_required
    def get(self):
        args = self.reqparse.parse_args()

        h5exts = ['h5', 'nxs']

        dc_filepath = get_filepath_from_dc(args.dcid)
        if dc_filepath is None:
            logging.getLogger('image-service').error('No such data collection {}'.format(args.dcid))
            abort(400, message='No such data collection')
        
        ext = os.path.splitext(str(dc_filepath))[1][1:].strip().lower()
        if ext in h5exts:
            file = str(dc_filepath)
        else:
            file = dc_filepath % args.image


        logging.getLogger('image-service').info('Processing image number: {} from file: {}'.format(args.image, file))
        
        if not os.path.exists(file):
            logging.getLogger('image-service').error('File not found: {}'.format(file))
            abort(400, message='No such file')

        datablocks = DataBlockFactory.from_filenames([file])
        if not len(datablocks):
            logging.getLogger('image-service').error('Could not parse data block')
            abort(400, message='Could not parse datablock')

        datablock = datablocks[0]
        imageset = datablock.extract_imagesets()[0]

        if ext in h5exts:
            image = imageset[(args.image-1):args.image]
        else:
            b0 = imageset.get_scan().get_batch_offset()
            image = imageset[b0:b0+1]

        params = phil_scope.extract()
        params.format = 'jpeg'

        if args.quality:
            params.jpeg.quality = args.quality

        if args.binning:
            params.binning = args.binning

        if args.threshold:
            params.display = 'threshold'
            params.brightness = 1000

        params.output.directory = '/tmp'
        params.output.prefix = str(time.time())
        params.imageset_index = 0
        names = imageset_as_bitmaps(image, params)

        @after_this_request
        def remove_file(response):
            for n in names:
                if os.path.exists(n):
                    os.remove(n)

            return response

        if args.threshold:
            thresh = Image.open(names[0])#.convert('RGBA')
            thresh = PIL.ImageOps.autocontrast(thresh, cutoff=50, ignore=(255,255,255))

            thresh.save(names[0], quality=100)


        return send_file(names[0])


api.add_resource(DataCollectionImage, '/dc/image')
