import os
import time

from PIL import Image
import PIL.ImageOps

import numpy as np

from flask import Blueprint, request, after_this_request, send_file
from flask_restful import Resource, Api, reqparse, abort
from flask_jwt_simple import jwt_required

from dxtbx.datablock import DataBlockFactory
from dials.command_line.export_bitmaps import imageset_as_bitmaps
from dials.command_line.export_bitmaps import phil_scope

from db import get_dc


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

        dc = get_dc(args.dcid)
        if dc is None:
            abort(400, message='No such data collection')
        
        ext = os.path.splitext(str(dc.file_template_full_python))[1][1:].strip().lower()
        if ext in h5exts:
            file = str(dc.file_template_full_python)
        else:
            file = dc.file_template_full_python % args.image


        print 'file', file, ext
        
        if not os.path.exists(file):
            abort(400, message='No such file')

        datablocks = DataBlockFactory.from_filenames([file], verbose=True)
        if not len(datablocks):
            abort(400, message='Could not parse datablock')

        datablock = datablocks[0]
        imageset = datablock.extract_imagesets()[0]

        if ext in h5exts:
            image = imageset[(args.image-1):args.image]
        else:
            image = imageset[0:1]

        params = phil_scope.extract()
        params.format = 'jpeg'

        if args.quality:
            params.jpeg.quality = args.quality

        if args.binning:
            params.binning = args.binning

        if args.threshold:
            params.display = 'threshold'
            params.brightness = 1000

        params.output_dir = '/tmp'
        params.prefix = str(time.time())
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

            # data = np.array(thresh)
            
            # Invert
            # data = 255 - data
            
            # Remove Red, Blue channels
            # data[:,:,0] *=0
            # data[:,:,2] *=0
            # data = 255 - data

            # Replace pixel value with another
            # red, green, blue, alpha = data.T
            # white_areas = (red == 255) & (blue == 255) & (green == 255)
            # data[..., :-1][white_areas.T] = (255, 255, 255)
            

            # thresh = Image.fromarray(data).convert('RGB')

            # Convert white to transparent
            # thresh2 = thresh2.convert('RGBA')
            # data = np.array(thresh2)
            # data[:, :, 3] = (255 * (data[:, :, :3] != 255).any(axis=2)).astype(np.uint8)
            # thresh2 = Image.fromarray(data)

            thresh.save(names[0], quality=100)


        return send_file(names[0])


api.add_resource(DataCollectionImage, '/dc/image')
