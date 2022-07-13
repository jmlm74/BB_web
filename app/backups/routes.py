import os
import subprocess
from flask import flash, make_response, redirect, render_template, jsonify, url_for
from app.backups import bp_backups
from app import app
from app.backups.models import Repo
from flask_api import status
from app.backups.forms import ArchiveFilterForm
from datetime import datetime, date


@bp_backups.route('/')
def login():
    return 'Hello'

@bp_backups.route('/bckp_detail/<id>')
def bckp_detail(id):
    repo = Repo.query.get_or_404(id)
    title = "Detail Repo " + repo.repo_name
    my_env = {**os.environ, 'PATH': '/usr/sbin:/sbin:/usr/bin:' + os.environ['PATH']}
    args = [app.config['BORG_BINARY']]
    args.append('--override')
    args.append(f"location.repositories=['{repo.repo_name}']")
    args.append('--override')
    args.append(f"storage.encryption_passphrase='{repo.repo_passphrase}'")
    args.append("info")
    rc = subprocess.run(args, capture_output=True, text=True, env=my_env)
    if rc.returncode != 0:
        ...
    repo_array = rc.stdout.split('\n')
    print(repo_array)
    try:
        array_ligne1 = repo_array[3].split(' ')
    except IndexError:
        flash("Erreur --> voir logs !")
        return redirect(url_for('index'))
    is_encrypted = True if array_ligne1[1] == 'Yes' else False
    ligne3 = repo_array[-4]
    array_ligne3 = repo_array[-4].split(' ')
    array_ligne3 = ' '.join(array_ligne3).split()

    context = {
        'repo_id': repo.id,
        'is_encrypted': is_encrypted,
        'original_size': array_ligne3[-6] + " " + array_ligne3[-5],
        'compressed_size': array_ligne3[-4] + " " + array_ligne3[-3],
        'deduplicated_size': array_ligne3[-2] + " " + array_ligne3[-1],
    }
    return render_template('bckp_detail.html', title=title, context=context)


@bp_backups.route('/archives_list/<id>')
def ajax_liste_archives(id):
    repo = Repo.query.get_or_404(id)

    my_env = {**os.environ, 'PATH': '/usr/sbin:/sbin:/usr/bin:' + os.environ['PATH']}
    args = [app.config['BORG_BINARY']]
    args.append('--override')
    args.append(f"location.repositories=['{repo.repo_name}']")
    args.append('--override')
    args.append(f"storage.encryption_passphrase='{repo.repo_passphrase}'")
    args.append("list")
    rc = subprocess.run(args, capture_output=True, text=True, env=my_env)
    if rc.returncode != 0:
        ...
    repo_array = rc.stdout.split('\n')
    print(repo_array)
    data = [get_data_from_archives_list(ligne, repo.id) for ligne in repo_array]
    # print(data)
    # remove None in array
    data = [i for i in data if i]
    # [repo_to_dict(repo) for repo in query]_
    # print(data)
    return {
        'data': data[1:],
        # [repo.to_dict() for repo in query],
    }

def get_data_from_archives_list(ligne, repo_id):
    if len(ligne) < 10:
        return None
    if ligne[0] == '/':
        return None
    ligne_array = ligne.split(' ')
    print(f"==={ligne_array}===")
    if len(ligne_array) < 4:
        archive_date = str(ligne_array[2])
        result = False
    else:
        if len(str(ligne_array[1])) == 0:
            date_archive = str(ligne_array[3])
            heure_archive = str(ligne_array[4])
        else:
            date_archive = str(ligne_array[2])
            heure_archive = str(ligne_array[3])            
        archive_date = date_archive + " - " + heure_archive
        str_archive_date = datetime.strptime(date_archive, "%Y-%m-%d").date()
        # print(date_archive)
        date_now = date.today()
        delta = date_now - str_archive_date
        if delta.days > 0:
            result = False
        else:
            result = True
        
    return {'id': repo_id,
            'archive_name': ligne_array[0][:40],
            'result': result,
            'archive_date': archive_date}


@bp_backups.route('/archive_info/<repo_id>/<archive_name>')
def archive_info(repo_id, archive_name):
    repo = Repo.query.get_or_404(repo_id)

    my_env = {**os.environ, 'PATH': '/usr/sbin:/sbin:/usr/bin:' + os.environ['PATH']}
    args = [app.config['BORG_BINARY']]
    args.append('--override')
    args.append(f"location.repositories=['{repo.repo_name}']")
    args.append('--override')
    args.append(f"storage.encryption_passphrase='{repo.repo_passphrase}'")
    args.append("--archive")
    args.append(archive_name)
    args.append("info")

    rc = subprocess.run(args, capture_output=True, text=True, env=my_env)
    if rc.returncode != 0:
        ...
    repo_array = rc.stdout.split('\n')
    # print(repo_array)
    data = [ligne for ligne in repo_array if ligne]
    print(data)
    print(data[-2])
    array_ligne = data[-2].split(' ')
    array_ligne = ' '.join(array_ligne).split()
    print(array_ligne)

    title = "Archive Info"
    context = {'repo_name': repo.repo_name,
               'archive_name': archive_name,
               'original_size': array_ligne[-6] + " " + array_ligne[-5],
               'compressed_size': array_ligne[-4] + " " + array_ligne[-3],
               'deduplicated_size': array_ligne[-2] + " " + array_ligne[-1],}
    return render_template('archive_info.html', title=title, context=context)


@bp_backups.route('/get_list_archive/<repo_id>/<archive_name>')
@bp_backups.route('/get_list_archive/<repo_id>/<archive_name>/<filter>')
def get_list_archive(repo_id, archive_name, filter=None):

    repo = Repo.query.get_or_404(repo_id)

    my_env = {**os.environ, 'PATH': '/usr/sbin:/sbin:/usr/bin:' + os.environ['PATH']}
    args = [app.config['BORG_BINARY']]
    args.append("list")
    args.append('--override')
    args.append(f"location.repositories=['{repo.repo_name}']")
    args.append('--override')
    args.append(f"storage.encryption_passphrase='{repo.repo_passphrase}'")
    args.append("--archive")
    args.append(archive_name)
    args.append("--short")
    if filter:
        args.append("--find")
        args.append(filter.replace("*", "/"))
    print(args)
    rc = subprocess.run(args, capture_output=True, text=True, env=my_env)
    if rc.returncode != 0:
        ...
    repo_array = rc.stdout.split('\n')
    # print(repo_array)
    data = [ligne for ligne in repo_array if ligne]
    if len(data) > 402:
        data = data[2:402]
    elif len(data) == 0:
        data = "Pas de fichier conrrespondant trouvé"
    else:
        data = data[2:]
    # print(data)
    data = {'data': data, }

    return make_response(jsonify(data, 200))


@bp_backups.route('/archive_filter/<repo_id>/<archive_name>', methods=['GET', 'POST'])
def archive_filter(repo_id, archive_name):
    repo = Repo.query.get_or_404(repo_id)
    form = ArchiveFilterForm()
    title = "Archive detail"
    context = {'repo_name': repo.repo_name,
               'archive_name': archive_name}
    if form.validate_on_submit():
        context['form_submit'] = True
        context['filter'] = form.filter.data.replace("/", "*")

    return render_template('archive_detail.html', title=title, context=context, form=form)