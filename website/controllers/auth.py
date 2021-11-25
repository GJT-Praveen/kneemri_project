from flask import Blueprint, render_template,request, flash, redirect
from flask_login.utils import login_required, logout_user,login_user
from website.utils.controller_utils import create_account, verify_login
# from website.utils.forms import login_form,signup_form



auth = Blueprint('auth',__name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        userid=request.form.get('userid')
        password=request.form.get('password')
        msg = verify_login(userid, password)
        if msg['category'] == 'error':
            flash(msg['msg'], msg['category'])
            return render_template('auth_login.html',boolean=True)
        else:
            flash(msg['msg'], msg['category'])
            login_user(msg['user'])
            if msg['usertype']=='Doctor':
                return redirect("/Dhome_Dashboard")
            else:
                return redirect('/Phome')

    return render_template('auth_login.html',boolean=True)



@auth.route('/Sign-up', methods=['GET','POST'])
def Sign_up():
    if request.method == 'POST':
        email=request.form.get('email')
        name=request.form.get('name')
        pnumber=request.form.get('pnumber')
        userid=request.form.get('userid')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        gender=request.form.get('gender')
        usertype=request.form.get('usertype')

        msg = create_account(name, userid, email,pnumber, password1, password2, gender, usertype)

        if msg['category'] == 'error':
            flash(msg['msg'], msg['category'])
            return render_template('auth_signup.html')

        else:
            flash(msg['msg'], msg['category'])
            return redirect('/login')
        
    return render_template('auth_signup.html')
    


@auth.route('/logout')
@login_required
def logout():
    logout_user
    return redirect('/')


