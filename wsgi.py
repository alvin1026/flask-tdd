"""
Web Server Gateway Interface (WSGI) entry point
"""

import os
from service import create_app

PORT = int(os.getenv("PORT", "8000"))
# FLASK_DEBUG = os.getenv("FLASK_DEBUG", False)

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
    # app.run(host="0.0.0.0", port=PORT, debug=True)
