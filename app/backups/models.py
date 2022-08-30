from app import app, db


class Repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repo_name = db.Column(db.String(180), unique=True, nullable=False)
    repo_passphrase = db.Column(db.String(50))
    repo_servername = db.Column(db.String(20), default="Servername")
    repo_active = db.Column(db.Boolean, default=True)
    repo_nb_days = db.Column(db.Integer, default=1)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def __repr__(self):
        return "<Repo : {}>".format(self.repo_name)

    def to_dict(self):
        return {
            'id': self.id,
            'repo_name': self.repo_name,
            'passphrase': self.repo_passphrase, }
