from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class ArchiveFilterForm(FlaskForm):
    filter = StringField('filter', validators=[DataRequired()],
                         description='Entrez le fichier/chemin recherché sans commencer par / et sans *' )
    submit = SubmitField('Rechercher')

    def validate_filter(self, filter):
        if filter.data[0] == "/":
            raise ValidationError("Erreur - Ne doit pas commencer par /")
        if filter.data[-1] == "*":
            raise ValidationError("Erreur - Ne doit pas terminer par *")