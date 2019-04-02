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
        # print dc.file_template_full_python
        # print dc.file_directory
        return dc

