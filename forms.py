from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField, SelectField, TimeField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import sqlite3
days = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31)
months = [(1,'january'),(2,'february'),(3,'march'),(4,'april'),(5,'may'),(6,'june'),(7,'july'),(8, 'august'),(9, 'september'),(10, 'october'),(11,'november'),(12, 'december'),]
years = [x for x in range(2021,2100)]
hours = [x for x in range(0,24)]
minutes = [x for x in range(0,60)]

class LoginForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	password = PasswordField('Password',validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

def validate_email(self, email):
	conn = sqlite3.connect('database.db')
	curs = conn.cursor()
	curs.execute("SELECT mail FROM user where mail = (?)",[email.data])
	valemail = curs.fetchone()
	if valemail is None:
		raise ValidationError('This Email ID is not registered. Please register before login')

class RegisterForm(FlaskForm):
	email = StringField('Email',validators=[DataRequired(),Email()])
	first = StringField('First',validators=[DataRequired()])
	last = StringField('Last', validators=[DataRequired()])
	password = PasswordField('Password',validators=[DataRequired(), EqualTo('confirm', message='Passwords not the same')])
	confirm = PasswordField('Confirm password',validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Register')

class Create_EventForm(FlaskForm):
	day = SelectField('Day', choices=days,validators=[DataRequired()])
	month = SelectField('Month', choices=months,validators=[DataRequired()])
	year = SelectField('Year', choices=years, validators=[DataRequired()])
	submit = SubmitField('Toevoegen')
	start_h = SelectField('Start', choices=hours, validators=[DataRequired()])
	start_m = SelectField('', choices=minutes, validators=[DataRequired()])
	end_h = SelectField('End', choices=hours, validators=[DataRequired()])
	end_m = SelectField('',choices=minutes,validators=[DataRequired()])
