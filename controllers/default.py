# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

def get_user_name_from_email(email):
    """Returns a string corresponding to the user first and last names,
    given the user email."""
    u = db(db.auth_user.email == email).select().first()
    if u is None:
        return 'None'
    else:
        return ' '.join([u.first_name, u.last_name])


def index():
    """
    This is your main controller.
    """
    # I am creating a bogus list here, just to have some divs appear in the
    # view.  You need to read at most 20 posts from the database, in order of
    # most recent first, and you need to return that list here.
    # Note that posts is NOT a list of strings in your actual code; it is
    # what you get from a db(...).select(...).
    posts = db().select(db.post.ALL,orderby=~db.post.created_on, limitby=(0,20))
    return dict(posts=posts)


@auth.requires_login()
def edit():
    """
    This is the page to create / edit / delete a post.
    """

    form = SQLFORM(db.post,request.args(0),deletable=True, showid=False)
    if request.args(0) is None:
        session.flash= T('testing')
    else:
        p = db((db.post.user_email == auth.user.email) & (db.post.id == request.args(0))).select().first()
        if p is None:
            session.flash = T('Access Denied')
            redirect(URL('default', 'index'))
    if form.accepts(request.vars,session):
        if not form.record:
            session.flash= T('posted')
        else:
            if form.vars.delete_this_record:
                session.flash = T('delete')
            else:
                session.flash = T('edited')
                db.post.update()
        redirect(URL('default', 'index'))
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()