"""
Site main resume content view.

URLs include:
/resume/
/resume/new/
/resume/<id>/
"""
import flask
import rsite
from rsite.model import show_username


@rsite.app.route('/resume/', methods=['GET'])
def show_resume():
    """Render react content for main resume page"""
    with rsite.app.app_context():
        context = show_username()
        return flask.render_template('resume.html', **context)


@rsite.app.route('/resume/new/')
def show_new():
    """Render react content for new resume page"""
    with rsite.app.app_context():
        context = show_username()
        if context['logname'] == "Sign In":
            return flask.redirect("/accounts/login")
        return flask.render_template('new.html', **context)


@rsite.app.route('/resume/<int:resumeid>/')
def show_saved(resumeid):
    """Render react content for view/edit resume page"""
    with rsite.app.app_context():
        context = show_username()

        logname = context['logname']
        if logname == "Sign In":
            flask.abort(403)

        database = rsite.model.get_db()
        cur = database.execute(
            "SELECT * "
            "FROM resumes "
            "WHERE resumeid == ?",
            (resumeid, )
        )
        resume = cur.fetchone()

        if resume['owner'] != logname:
            flask.abort(403)

        return flask.render_template('view_edit.html', **context)

@rsite.app.route('/resume/commit/', methods=['POST'])
def post_resumes():
    """Resolve post requests for the resume."""
    database = rsite.model.get_db()

    logname = rsite.model.get_logname()
    if not logname:
        flask.abort(403)

    op = flask.request.args.get("operation", default=None, type=str)

    if op is None:
        flask.abort(404)

    if op == "create":
        # get name and type of resume
        rname = flask.request.form.get('name')
        rtype = flask.request.form.get('type')
        
        if len(rname) == 0:
            flask.abort(400)
        
        rtype = 1 if rtype == 'on' else 0
        
        cur = database.execute(
            "INSERT INTO resumes "
            "(owner, name, typename) "
            "VALUES (?, ?, ?)",
            (logname, rname, rtype, )
        )
        cur.fetchone()

    elif op == "delete":
        rid = flask.request.form.get("id", default=0, type=int)
        if rid == 0:
            flask.abort(404)
        # first delete/update the entries. load them using the intermediate table
        cur = database.execute(
            "SELECT * "
            "FROM resume_to_entry "
            "WHERE resumeid == ?",
            (rid, )
        )
        eids = cur.fetchall()
        for eid in eids:
            # fetch the entry
            cur = database.execute(
                "SELECT * "
                "FROM entries "
                "WHERE entryid == ?",
                (eid['entryid'], )
            )
            entry = cur.fetchone()

            if logname != entry['owner']:
                flask.abort(403)

            entry['frequency'] = entry['frequency'] - 1
            if entry['frequency'] == 0:
                # delete the entry
                cur = database.execute(
                    "DELETE FROM entries "
                    "WHERE entryid == ?",
                    (entry['entryid'],)
                )

            else:
                # update the entry
                cur = database.execute(
                    "UPDATE entries "
                    "SET frequency = ?"
                    "WHERE entryid == ?",
                    (entry['frequency'], entry['entryid'],)
                )
            
            # execute the update/delete for this entry
            cur.fetchone()

        # then delete the resume
        cur = database.execute(
            "DELETE FROM resumes "
            "WHERE resumeid == ?"
            "AND owner == ?",
            (rid, logname, )
        )
        cur.fetchone()

    elif op == "save":
        pass

    target = rsite.model.get_target()

    return flask.redirect(target)