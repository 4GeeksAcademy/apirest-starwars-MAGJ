import os
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, Planet, People, Favorite


class FavoriteAdmin(ModelView):
    # forzar lista y formularios
    column_list = ("id", "user", "planet", "people")
    form_columns = ("user", "planet", "people")

    column_searchable_list = ("user.email",)
    column_filters = ("planet.name", "people.name")


def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'

    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(FavoriteAdmin(Favorite, db.session))
