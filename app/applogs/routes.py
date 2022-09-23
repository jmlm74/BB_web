from app.applogs import bp_applogs
from app.backups.models import Repo
from paramiko import SSHClient
from scp import SCPClient, SCPException
import uuid
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

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=ssh_server, username=username)
    with SCPClient(ssh.get_transport()) as scp:
        try:
            scp.get(fichier_log, local_path=local_fichier_log)
            scp.put(local_fichier_log)
        except SCPException as e:
            print(f"ERROR scp - {e}")
            flash(f"Erreur download fichier log {local_fichier_log}")
            return render_template('showlog.html', title=title, context=context)
    
    '''
    sftp_client = ssh.open_sftp()
    remote_file = sftp_client.open(fichier_log)
    try:
        ficlog_array = []
        for line in remote_file:
            if len(line) > 0:
                line = line.strip()
                print(f"---{line}---")
                ficlog_array.append(line)
    finally:
        remote_file.close()
    '''
    context['ficlog'] = fichier_log
    context['server'] = repo.repo_servername
    context['local_fichier_log_url'] = 'http://' + request.host + '/tmp/' + local_nomfichier_log
    # context['ficlog_array'] = ficlog_array
    return render_template('showlog.html', title=title, context=context)
