import os
import re

import ispyb.sqlalchemy
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(ispyb.sqlalchemy.url(), connect_args={"use_pure": True})
Session = sessionmaker(bind=engine)

logger = logging.getLogger("image-service")


def get_file_template_full(dcid):
    """
    From dials 3.4+ found that the mxaquisition object not working
    So this simpler version uses a different method to get datacollection info
    and only returns the filepath of interest
    """

    from ispyb.sqlalchemy import DataCollection

    with Session() as session:
        query = session.query(
            DataCollection.imageDirectory, DataCollection.fileTemplate
        ).filter(DataCollection.dataCollectionId == dcid)
        dc = query.first()
    if not dc:
        logger.warning(f"Couldn't find data collection {dcid}")
    file_template_full = os.path.join(dc.imageDirectory, dc.fileTemplate)
    if "#" in file_template_full:
        file_template_full = re.sub(
            r"#+",
            lambda x: "%%0%dd" % len(x.group(0)),
            file_template_full.replace("%", "%%"),
            count=1,
        )
    return file_template_full
