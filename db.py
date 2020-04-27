import os
import re
import ispyb
import logging


def file_template_full(file_directory, file_template):
    return os.path.join(file_directory, file_template)

def file_template_full_python(file_template_full):
    if not file_template_full:
        return None
    if "#" not in file_template_full:
        return file_template_full
    return re.sub(
        r"#+",
        lambda x: "%%0%dd" % len(x.group(0)),
        file_template_full.replace("%", "%%"),
        count=1,
    )

def get_dc(id):
    conf_file = os.getenv('ISPYB_CONFIG_FILE')
    if conf_file is None:
        return

    with ispyb.open(conf_file) as i:
        mx_acquisition = i.mx_acquisition
        
        dc = mx_acquisition.retrieve_data_collection(id)
        dc = dc[0]

        dc['file_template_full'] = file_template_full(dc['imgDir'], dc['fileTemplate'])
        dc['file_template_full_python'] = file_template_full_python(dc['file_template_full'])

        logging.getLogger('image-service').debug('DC File Template: {}'.format(dc['file_template_full_python']))
        logging.getLogger('image-service').debug('DC File Directory: {}'.format(dc['imgDir']))

        return dc
