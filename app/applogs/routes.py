from app.applogs import bp_applogs
from app.backups.models import Repo
from paramiko import SSHClient
from scp import SCPClient, SCPException
import uuid
import pysftp, paramiko
from flask import render_template, request, flash
from app import app

@bp_applogs.route('/showlog/<repo_id>', methods=['GET', ])
def showlog(repo_id):
    repo = Repo.query.get_or_404(repo_id)
    print(f"{repo} ")
    title = repo.repo_name
    context = {}
    # Get logfile
    fichier_log = repo.repo_name[:-4]
    pos_last_slash = fichier_log.rfind('/')
    fichier_log = app.config['BORG_LOG_PATH'] + fichier_log[pos_last_slash:] + 'log'
    at_pos = repo.repo_name.find("@")
    semicolon_pos = repo.repo_name.find(":")
    ssh_server = repo.repo_name[at_pos + 1:semicolon_pos]
    username = repo.repo_name[:at_pos]
    local_nomfichier_log = str(uuid.uuid4()) + '.txt'
    local_fichier_log = app.config['TMPDIR'] + "/" + local_nomfichier_log
    print(f"LOGFILE:{fichier_log} - ssh_server : {ssh_server} - username : {username} - LF : {local_fichier_log} ")

    # my_key = paramiko.Ed25519Key.from_private_key_file("/root/.ssh/id_ed25519")
    # my_key = paramiko.Ed25519Key.get_fingerprint("/root/.ssh/id_ed25519")
    with pysftp.Connection(ssh_server, username=username, private_key="/root/.ssh/id_rsa") as sftp:
        try:
            sftp.get(fichier_log, local_fichier_log)
        except SCPException as e:
            print(f"ERROR scp - {e}")
            flash(f"Erreur download fichier log {local_fichier_log}")
            return render_template('showlog.html', title=title, context=context)
    context['ficlog'] = fichier_log
    context['server'] = repo.repo_servername
    print(request.url)
    if request.url.find("https") == -1 and request.url.find("127.0.0.1") != -1:
        protocole = "http://"
    else:
        protocole = "https://"
    context['local_fichier_log_url'] = protocole + request.host + '/tmp/' + local_nomfichier_log
    # context['ficlog_array'] = ficlog_array
    return render_template('showlog.html', title=title, context=context)
