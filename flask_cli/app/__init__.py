import data
app = None

def create_app () :
    from flask import Flask
    app = Flask(__name__)

    import config
    app.config.from_object('config')

    db = data.init_app(app)

    from app import admin
    admin.init_app(app,db)

    with app.app_context():
        from app import views
        app.register_blueprint(views.bp,url_prefix='/')

        return app
