# This file starts the WSGI web application.
# - Heroku starts gunicorn, which loads Procfile, which starts run.py
# - Developers can run it from the command line: python run.py

from ibwt.app_and_db import app, db
from ibwt.startup.init_app import init_app

init_app(app, db)

# Start a development web server if executed from the command line
if __name__ == "__main__":
    import ssl
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain('/etc/nginx/ssl/nginx.crt',
                            '/etc/nginx/ssl/nginx.key')
    app.run(host='0.0.0.0',
        port=443, debug=True,
        ssl_context=context)
