import os
from app import create_app


if __name__ == '__main__':
    os.environ["DATAVIEWER_SETTINGS"] = "settings.cfg"
    os.environ["ISPYB_CONFIG_FILE"] = "test.cfg"

    app = create_app()
    app.run(debug=True, port=5000)
