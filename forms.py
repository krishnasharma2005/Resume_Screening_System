from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class UploadResumeForm(FlaskForm):
    resume = FileField('Upload Resume (PDF or DOCX)', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'docx'], 'PDF or DOCX files only!')
    ])
    job_posting = SelectField('Select Job Posting', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Upload and Analyze')

class JobPostingForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    keywords = TextAreaField('Keywords (comma separated)', validators=[DataRequired()])
    submit = SubmitField('Create Job Posting')
