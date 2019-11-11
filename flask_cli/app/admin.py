from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, request
from flask_admin.model import typefmt
from datetime import datetime

class AdminView(ModelView):
    can_edit = True
    edit_modal = True
    create_modal = True
    can_export = True
    can_view_details = True
    details_modal = True

    column_editable_list = ['username']
    column_searchable_list = column_editable_list
    column_filters = column_editable_list

    def is_accessible(self):
        return True
        return session.get('user') == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('home', next=request.url))

class TopicView(AdminView):
    def __init__(self, *args, **kwargs):
        super(TopicView, self).__init__(*args, **kwargs)

    column_list = ('title', 'date_created', 'date_modified', 'total_vote_count', 'status')
    column_searchable_list = ('title',)
    column_default_sort = ('date_created', True)
    column_filters = ('status',)
    column_sortable_list = ('total_vote_count',)

from flask_admin import Admin

from flask import url_for
from data import Users
def init_app(app,db):
    adm = Admin(app, name='DATABASE', template_mode='bootstrap3')
    adm.add_view(AdminView(Users, db.session))

    @app.context_processor
    def inject_url():
        return dict(
             admin_view=adm.index_view,
             get_url=url_for
         )

    return adm
