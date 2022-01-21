#!/usr/bin/env python3

import dotenv
from netbook.server import create_app

dotenv.load_dotenv()
create_app().run(debug=True)
