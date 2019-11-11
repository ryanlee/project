#!/usr/bin/env python
# Run a test server.
from app import create_app
create_app().run(host='0.0.0.0', port=5000, debug=True)
