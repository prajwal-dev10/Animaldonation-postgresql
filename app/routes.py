from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    flash,
    url_for,
    abort,
    get_flashed_messages,
    current_app
)

from flask_login import (
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.utils import secure_filename

from bcrypt import hashpw, checkpw, gensalt

import os


from .extensions import db, login_manager
from .models import Animal, User, Event, Donate


# change this import based on your location
from forms import (
    AnimalForm,
    LoginForm,
    SignupForm,
    addeventForm,
    DonationForm
)


main = Blueprint("main", __name__)


# -----------------------------
# LOGIN MANAGER
# -----------------------------

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(int(user_id))



@login_manager.unauthorized_handler
def unauthorized_callback():

    return redirect(
        url_for("main.login")
    )



# -----------------------------
# USER CREATION
# -----------------------------

def add_user(
    username,
    password,
    email,
    is_admin=False
):

    new_user = User(
        username=username,
        password=password,
        email=email,
        is_admin=is_admin
    )


    db.session.add(new_user)

    db.session.commit()


    return new_user



# -----------------------------
# HOME
# -----------------------------

@main.route("/")
def home():


    if current_user.is_anonymous:

        user = "Guest"

    else:

        user = current_user.username



    animals = Animal.query.order_by(
        Animal.id.desc()
    ).limit(3).all()



    events = Event.query.order_by(
        Event.date.desc()
    ).limit(3).all()



    messages = get_flashed_messages()



    return render_template(
        "index.html",
        animals=animals,
        events=events
    )



# -----------------------------
# ADD ANIMAL
# -----------------------------

@main.route(
    "/addanimal",
    methods=["GET","POST"]
)
def addanimal():


    form = AnimalForm()



    if form.validate_on_submit():


        file = form.image.data


        filename = secure_filename(
            file.filename
        )



        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )


        file.save(filepath)



        new_animal = Animal(

            name=form.name.data,

            catagory=form.catagory.data,

            description=form.description.data,

            image=filename
        )



        db.session.add(new_animal)

        db.session.commit()



        return redirect(
            url_for("main.showanimals")
        )



    return render_template(
        "addanimal.html",
        form=form
    )



# -----------------------------
# SHOW ANIMALS
# -----------------------------

@main.route("/animal")
def showanimals():


    catagory = request.args.get(
        "catagory"
    )


    page = request.args.get(
        "page",
        1,
        type=int
    )



    query = Animal.query



    if catagory and catagory != "all":

        query = query.filter_by(
            catagory=catagory
        )



    animals = query.paginate(
        page=page,
        per_page=5
    )



    return render_template(
        "animal.html",
        animals=animals,
        catagory=catagory
    )
@main.route('/login', methods=['GET','POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()


    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data


        password_bytes = password.encode("utf-8")


        user = User.query.filter_by(
            username=username
        ).first()


        if user and checkpw(
            password_bytes,
            user.password.encode("utf-8")
        ):

            login_user(user)

            flash("Login successful")

            return redirect(
                url_for("main.home")
            )


        flash(
            "Invalid username or password"
        )


    messages = get_flashed_messages()


    return render_template(
        "login.html",
        messages=messages,
        form=form
    )





@main.route('/logout')
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully"
    )

    return redirect(
        url_for("main.home")
    )





@main.route('/signup', methods=['GET','POST'])
def signup():


    form = SignupForm()


    if form.validate_on_submit():


        username = form.username.data

        password = form.password.data

        email = form.email.data



        existing_user = User.query.filter_by(
            username=username
        ).first()


        if existing_user:

            flash(
                "Username already exists"
            )

            return redirect(
                url_for("main.signup")
            )



        # first registered user becomes admin
        is_admin = False

        if User.query.count() == 0:
            is_admin = True



        password_hash = hashpw(
            password.encode("utf-8"),
            gensalt()
        ).decode("utf-8")



        user = User(

            username=username,

            password=password_hash,

            email=email,

            is_admin=is_admin

        )



        db.session.add(user)

        db.session.commit()



        login_user(user)


        flash(
            "Account created successfully"
        )


        return redirect(
            url_for("main.home")
        )



    messages = get_flashed_messages()


    return render_template(
        "signup.html",
        messages=messages,
        form=form
    )







@main.route('/event')
def showevents():


    page = request.args.get(
        "page",
        1,
        type=int
    )


    events = Event.query.order_by(
        Event.date.desc()
    ).paginate(
        page=page,
        per_page=5
    )


    return render_template(
        "event.html",
        events=events
    )







@main.route("/addevent", methods=['GET','POST'])
@login_required
def addevent():


    if not current_user.is_admin:

        abort(403)



    form = addeventForm()



    if form.validate_on_submit():


        file = form.image.data


        filename = secure_filename(
            file.filename
        )


        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )


        file.save(filepath)



        event = Event(

            eventname=form.eventname.data,

            date=form.date.data,

            description=form.description.data,

            image=filename

        )



        db.session.add(event)

        db.session.commit()



        flash(
            "Event added successfully"
        )


        return redirect(
            url_for("main.showevents")
        )




    return render_template(
        "addevent.html",
        form=form
    )


# -----------------------------
# DONOR REQUEST LIST
# -----------------------------

@main.route(
    "/donorrequest",
    methods=["GET","POST"]
)
@login_required
def donorlist():


    if not current_user.is_admin:

        flash(
            "access denied"
        )

        return redirect(
            url_for("main.home")
        )



    donors = Donate.query.all()



    return render_template(
        "donorrequest.html",
        donors=donors
    )





# -----------------------------
# DONATION FORM
# -----------------------------

@main.route(
    "/donationform",
    methods=["GET","POST"]
)
@login_required
def donationform():


    form = DonationForm()



    if form.validate_on_submit():


        file = form.Image.data


        filename = secure_filename(
            file.filename
        )



        filepath = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )


        file.save(filepath)



        donation = Donate(

            Firstname=form.Firstname.data,

            Lastname=form.Lastname.data,

            Address=form.Address.data,

            Email=form.Email.data,

            Image=filename,

            Amount=form.Amount.data

        )



        db.session.add(donation)

        db.session.commit()



        flash(
            "Donation request submitted"
        )



        return redirect(
            url_for("main.home")
        )




    return render_template(
        "donationForm.html",
        form=form
    )







# -----------------------------
# DELETE ANIMAL
# -----------------------------

@main.route(
    "/delete_animal/<int:animal_id>",
    methods=["POST"]
)
@login_required
def delete_animal(animal_id):


    if not current_user.is_admin:

        abort(403)



    animal = Animal.query.get_or_404(
        animal_id
    )



    db.session.delete(animal)

    db.session.commit()



    flash(
        "Animal deleted successfully!"
    )



    return redirect(
        url_for("main.showanimals")
    )







# -----------------------------
# EDIT ANIMAL
# -----------------------------

@main.route(
    "/edit_animal/<int:animal_id>",
    methods=["GET","POST"]
)
@login_required
def edit_animal(animal_id):


    if not current_user.is_admin:

        abort(403)



    animal = Animal.query.get_or_404(
        animal_id
    )



    form = AnimalForm(
        obj=animal
    )



    if form.validate_on_submit():


        animal.name = form.name.data

        animal.catagory = form.catagory.data

        animal.description = form.description.data




        if form.image.data:


            file = form.image.data


            filename = secure_filename(
                file.filename
            )



            filepath = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                filename
            )



            file.save(filepath)



            animal.image = filename




        db.session.commit()



        flash(
            "Animal updated successfully!"
        )



        return redirect(
            url_for("main.showanimals")
        )




    return render_template(
        "edit_animal.html",
        form=form,
        animal=animal
    )







# -----------------------------
# DELETE EVENT
# -----------------------------

@main.route(
    "/event/delete/<int:id>",
    methods=["POST"]
)
@login_required
def delete_event(id):


    if not current_user.is_admin:

        abort(403)



    event = Event.query.get_or_404(
        id
    )



    db.session.delete(event)

    db.session.commit()



    flash(
        "Event deleted successfully!"
    )



    return redirect(
        url_for("main.showevents")
    )







# -----------------------------
# DELETE DONOR
# -----------------------------

@main.route(
    "/donor/delete/<int:id>",
    methods=["POST"]
)
@login_required
def delete_donor(id):


    if not current_user.is_admin:

        abort(403)



    donor = Donate.query.get_or_404(
        id
    )



    db.session.delete(donor)

    db.session.commit()



    flash(
        "Donor deleted successfully!"
    )



    return redirect(
        url_for("main.donorlist")
    )
@main.route("/health")
def health():
    return {
        "status": "ok"
    }, 200