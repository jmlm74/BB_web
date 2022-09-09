import imp
import os
import subprocess
from time import strptime
from flask import redirect, render_template, make_response, request, url_for
from app import app, db
from app.backups.models import Repo
from datetime import datetime, date

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    repos = Repo.query.all()
    context = {'repos': repos}
    r = make_response(render_template('index.html', title='Index', context=context))

    return r


@app.route('/repos_list')
def ajax_liste_users():
    query = Repo.query.filter_by(repo_active=True)
    server_name = "toto"

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Repo.repo_name.like(f'%{search}%'),
        ))

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['repo_name']:
            col_name = 'repo_name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Repo, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    total_filtered = query.count()

    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)
    data = [repo_to_dict(repo) for repo in query]
    print(data)
    return {
        'data': data,
        # [repo.to_dict() for repo in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Repo.query.count(),
        'draw': request.args.get('draw', type=int),
    }

def repo_to_dict(repo):
    server_name = repo.repo_servername
    my_env = {**os.environ, 'PATH': '/usr/sbin:/sbin:/usr/bin:' + os.environ['PATH']}
    args = [app.config['BORG_BINARY']]
    args.append('--override')
    args.append(f"location.repositories=['{repo.repo_name}']")
    args.append('--override')
    args.append(f"storage.encryption_passphrase='{repo.repo_passphrase}'")
    args.append("list")
    args .append("--last")
    args.append("1")
    rc = subprocess.run(args, capture_output=True, text=True, env=my_env)
    if rc.returncode != 0:
        print(f"ERREUR {args} - {rc.stdout} - {rc.stderr}")
        return {'id': repo.id,
                'server_name': server_name,
                'repo_name': repo.repo_name,
                'repo_last_archive': "ERREUR !",
                'result': False, }

    print(f"---{rc.stdout}---")
    if rc.stdout.count('\n') == 1:
        # pas de sauvegardes !
        return {
            'id': repo.id,
            'server_name': server_name,
            'repo_name': repo.repo_name,
            'repo_last_archive': "1900-01-01",
            'result': False,
        }
    date_archive_str = rc.stdout.split()[-3]
    time_archive_str = rc.stdout.split()[-2]
    repo_last_archive = date_archive_str + " - " + time_archive_str
    date_archive = datetime.strptime(date_archive_str, "%Y-%m-%d").date()
    date_now = date.today()
    delta = date_now - date_archive
    if delta.days > repo.repo_nb_days:
        result = False
    else:
        result = True
    print(f"{repo.repo_name} - {server_name}")
    return {'id': repo.id,
            'server_name': server_name,
            'repo_name': repo.repo_name,
            'repo_last_archive': repo_last_archive, 
            'result': result, }
