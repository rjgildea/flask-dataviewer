import os
import ispyb
import logging


def get_dc(id):
    conf_file = os.getenv('ISPYB_CONFIG_FILE')
    if conf_file is None:
        return

    with ispyb.open(conf_file) as i:
        mx_acquisition = i.mx_acquisition
        
        dc = mx_acquisition.get_data_collection(id)

        logging.getLogger('image-service').debug('DC File Template: {}'.format(dc.file_template_full_python))
        logging.getLogger('image-service').debug('DC File Directory: {}'.format(dc.file_directory))

        return dc

def get_filepath_from_dc(id):
    """
    From dials 3.4+ found that the mxaquisition object not working
    So this simpler version uses a different method to get datacollection info
    and only returns the filepath of interest
    """
    filepath = None

    conf_file = os.getenv('ISPYB_CONFIG_FILE')
    if conf_file is None:
        return

    with ispyb.open(conf_file) as i:
        mx_acquisition = i.mx_acquisition

        records = mx_acquisition.retrieve_data_collection(id)

        try:
            filepath = os.path.join(records[0]['imgDir'], records[0]['fileTemplate'])
            logging.getLogger('image-service').debug('DC File Template: {}'.format(filepath))
        except TypeError:
            logging.getLogger('image-service').error('No result from retrieve data collection for id: {}'.format(id))
        except IndexError:
            logging.getLogger('image-service').error('Result from retrieve data collection out of bounds for id: {}'.format(id))

        return filepath