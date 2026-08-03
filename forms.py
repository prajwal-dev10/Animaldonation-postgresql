from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,TextAreaField,SelectField,DateField,IntegerField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField,FileAllowed

class AnimalForm(FlaskForm):
    name = StringField("Animal Name",validators=[DataRequired()])
    catagory = SelectField("category",choices=[  ("dog", "Dog"),
        ("cat", "Cat"),
        ("lion", "Lion"),
        ("tiger", "Tiger"),
        ("bird", "Bird"),])
    description = TextAreaField("Description",validators = [DataRequired()])
    image = FileField('Image',validators=[FileAllowed(["jpg","png","jpeg","gif"],"Images only!")])
    submit = SubmitField('Upload')



class LoginForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()]) 
    password = PasswordField('Password',validators=[DataRequired()])
    
    submit = SubmitField('Log in')

class SignupForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])    
    password = PasswordField('Password',validators=[DataRequired()])
    email = StringField('email',validators=[DataRequired()])
    submit = SubmitField('Sign up')


class addeventForm(FlaskForm):
    eventname = StringField('Eventname',validators = [DataRequired()])
    date = DateField('Date',validators = [DataRequired()])
    description = TextAreaField('Description',validators = [DataRequired()])
    image = FileField('Image',validators=[DataRequired(),FileAllowed(["jpg","png","jpeg","gif"],"Images only!")])
    submit = SubmitField('Upload')


class DonationForm(FlaskForm):
    Firstname = StringField('Firstname',validators=[DataRequired()])
    Lastname = StringField('Lastname',validators=[DataRequired()])
    Address = StringField('Address',validators=[DataRequired()])
    Email = StringField('Email',validators=[DataRequired()])
    Image = FileField('Screenshot of Amount that you have donated !',validators=[DataRequired(),FileAllowed(["jpg","png","jpeg","gif"],"Upload your statement ")])
    Amount = IntegerField('Amount you have donated',validators=[DataRequired()])
    submit = SubmitField('Donate')
    




    