from flask import Flask ,redirect,render_template,flash,request,get_flashed_messages,url_for,abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed

from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from flask_login import LoginManager,login_user,login_required,logout_user,current_user,UserMixin

from bcrypt import hashpw,checkpw,gensalt
from forms import AnimalForm,LoginForm,SignupForm,addeventForm,DonationForm
from dotenv import load_dotenv
import os
from .models import Animal, User, Event, Donate

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@db:5432/animaldb"
)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "dev-secret-key-change-in-production"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["WTF_CSRF_ENABLED"] = True
app.config["UPLOAD_FOLDER"] = "static/uploads"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)

def create_app_context():
    with app.app_context():
        db.create_all()



    def __repr__(self):
        return f'<user> {self.username}'
    
def add_user(username, password, email, is_admin=False):
    new_user = User(
        username=username,
        password=password,
        email=email,
        is_admin=is_admin
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user 


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')




@app.route('/')
def home():
    if current_user.is_anonymous:
        user = "Guest"
    else:
        user = current_user.username
    animals = Animal.query.order_by(Animal.id.desc()).limit(3).all()
    events = Event.query.order_by(Event.date.desc()).limit(3).all()    
    messages = get_flashed_messages()        

    return render_template("index.html",animals=animals,events=events)

@app.route("/addanimal",methods=['GET','POST'])
def addanimal():
    form = AnimalForm()
    if form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"],filename)
        file.save(filepath)  

        new_animal = Animal(
            name = form.name.data,
            catagory = form.catagory.data,
            description = form.description.data,
            image = filename
            
        )
        db.session.add(new_animal)
        db.session.commit()

        return redirect(url_for("showanimals"))
    
    return render_template("addanimal.html",form=form)


@app.route("/animal")
def showanimals():
    catagory = request.args.get("catagory") #using get for filtering so it dont need validationonclick
    page = request.args.get("page",1,type = int )
    query = Animal.query

    if catagory and catagory !="all":
        animals = query.filter_by(catagory=catagory)
    

    animals = query.paginate(page = page,per_page = 5)


    return render_template("animal.html",animals=animals,catagory = catagory)


@app.route('/login',methods= ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('All field are required')
            messages = get_flashed_messages()
            return render_template('login.html',messages = messages)

        username = form.username.data
        password = form.password.data
        password_bytes = password.encode('utf-8')
      #get entered password of user
        user = User.query.filter_by(username=username).first()
        if not user:
            pass
        elif checkpw(password_bytes,user.password):
            login_user(user)
            return redirect('/')
        flash('Invalid username or password')

    messages = get_flashed_messages()
    return render_template('login.html',messages=messages,form=form)    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')    

@app.route('/signup',methods = ['GET','POST'])
def signup():
    is_admin = False
    if User.query.count() == 0:
        is_admin = True
    form = SignupForm()
    if request.method == 'POST':
        if not form.validate_on_submit():
            flash('All field are required')
            messages = get_flashed_messages()
            return render_template('signup.html',messages=messages)

        username = form.username.data
        password = form.password.data
        email = form.email.data
        password_bytes = password.encode('utf-8')

        salt = gensalt()
        password = hashpw(password_bytes,salt)

        user = User.query.filter_by(username=username).first()
        if user is not None:
            flash('Username is already taken')
        else:
            user = add_user(username,password,email,is_admin)
            flash('successfully created account')
            login_user(user)
            return redirect('/')   

    messages = get_flashed_messages()
    return render_template('signup.html',messages=messages,form=form) 

@app.route('/event',methods = ['GET','POST'])
def showevents():
   page = request.args.get("page",1,type = int)

   query = Event.query.order_by(Event.date.desc())
   events = query.paginate(page=page,per_page= 5)

   return render_template("event.html",events=events)



@app.route("/addevent",methods=['GET','POST'])
def addevent():
    if not current_user.is_admin:
        flash("access denied")
        return redirect(url_for("showevents"))
    form = addeventForm()
    if form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"],filename)
        file.save(filepath)  

        new_event = Event(
            eventname = form.eventname.data,
            date = form.date.data,
            description = form.description.data,
            image = filename
            
        )
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for("showevents"))
    
    return render_template("addevent.html",form=form)

@app.route("/donorrequest", methods = ['GET','POST'])
def donorlist():
    if not current_user.is_admin:
        flash("access denied")
        return redirect(url_for("home"))
    else:    
        donors = Donate.query.all()
        return render_template("donorrequest.html", donors = donors)
    


@app.route("/donationform",methods=['GET','POST'])
def donationform():
    if not current_user.is_authenticated:
        flash("access denied, you need to login forst")
        return redirect(url_for("login"))
    form = DonationForm()
    if form.validate_on_submit():
        file = form.Image.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"],filename)
        file.save(filepath)  

        new_donation = Donate(
            Firstname = form.Firstname.data,
            Lastname = form.Lastname.data,
            Address = form.Address.data,
            Email = form.Email.data,
            Image = filename,
            Amount = form.Amount.data

            
        )
        db.session.add(new_donation)
        db.session.commit()

        return redirect(url_for("donorlist"))
    
    return render_template("donationForm.html",form=form)




@app.route("/delete_animal/<int:animal_id>", methods=["POST"])
@login_required
def delete_animal(animal_id):
    if not current_user.is_admin:
        abort(403)

    animal = Animal.query.get_or_404(animal_id)
    db.session.delete(animal)
    db.session.commit()

    flash("Animal deleted successfully!")
    return redirect(url_for("showanimals"))


@app.route("/edit_animal/<int:animal_id>", methods=["GET", "POST"])
@login_required
def edit_animal(animal_id):
    if not current_user.is_admin:
        abort(403)

    animal = Animal.query.get_or_404(animal_id)
    form = AnimalForm(obj=animal)

    if form.validate_on_submit():
        # update text fields
        animal.name = form.name.data
        animal.catagory = form.catagory.data
        animal.description = form.description.data

        # update image only if user uploads new one
        if form.image.data and hasattr(form.image.data, "filename"):
            file = form.image.data
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
            animal.image = filename

        db.session.commit()
        flash("Animal updated successfully!")
        return redirect(url_for("showanimals"))

    return render_template("edit_animal.html", form=form, animal=animal)

@app.route("/event/delete/<int:id>", methods=["POST"])
@login_required
def delete_event(id):

    if not current_user.is_admin:
        abort(403)

    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()

    flash("Event deleted successfully!")
    return redirect(url_for("showevents"))

@app.route("/donor/delete/<int:id>", methods=["POST"])
@login_required
def delete_donor(id):

    if not current_user.is_admin:
        abort(403)

    donor = Donate.query.get_or_404(id)
    db.session.delete(donor)
    db.session.commit()

    flash("Donor deleted successfully!")
    return redirect(url_for("donorlist"))

if __name__ == '__main__':
    if not os.path.exists("static/uploads"):
       os.makedirs("static/uploads") 
    create_app_context()   
    app.run(debug=True)







