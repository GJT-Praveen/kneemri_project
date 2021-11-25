from flask import current_app
from website.controllers import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,current_user
from website.models.user_list import User
from functools import wraps
from flask_login import LoginManager

def checkemail(a):
    count = 0
    for letter in a:
        if letter=='@'or letter==".":
            count+=1
    if(count==2): return False
    else: return True

def create_account(name, userid, email, pnumber, password1, password2, gender, usertype):

    if len(name)<3:
        msg = {'msg':"Name should be greater than 2 characters",'category':'error'} 
    
    elif checkemail(email):
        msg = {'msg':"Email incorrect",'category':'error'} 
    
    elif len(password1)<8:
        msg = {'msg':"Password too short",'category':'error'} 
    
    elif password1!=password2:
        msg = {'msg':"Passwords donot match",'category':'error'}    
    
    elif db.get_user_for_email(email):
        msg = {'msg':"Email already in use",'category':'error'}

    elif db.get_user_for_userid(userid)[0]['userid']==userid:
        msg = {'msg':"UserID already in use",'category':'error'}
    
    else:
        password = generate_password_hash(password1)
        print(usertype)
        db.create_new_user(name, userid, email, pnumber, password, gender, usertype)
        msg = {'msg':"Account created!!",'category':'success'}
        
    return msg


def verify_login(userid, password):

    result = db.get_user_for_userid(userid)
    
    if result[0]['userid']==userid:
        user = User(**result[0])
        if check_password_hash(user.password, password):
            
            if user.usertype == 'Doctor':
                msg= {"msg":"Logged in Succesfully", 'category':'success', 'usertype': 'Doctor','user':user}
                
            else:
                msg= {"msg":"Logged in Succesfully", 'category':'success', 'usertype': 'Patient','user':user}
                

        else:
            msg= {"msg":"Incorrect Password", 'category':'error','user':None}
    else:

        msg= {"msg":"UserID not registered", 'category':'error','user':None}
    
    return msg

def add_patient_data(patientid, doctorid, name, email, pnumber, gender,abnormal,acl,meniscus):
    result=db.get_patients_for_doctorid(doctorid)
    for row in result:
        if row['patientid']==patientid:
            msg={"msg":"Patient already added", "category":"error"}
            return msg
    db.add_new_patient(patientid,doctorid,name,email,pnumber,gender,abnormal,acl,meniscus)
    msg={'msg':'Patient added succesfully',"category":'success'}
    return msg

def delete_patient_data(doctorid,patientid):
    db.delete_patient(doctorid,patientid)
    msg ={'msg':'Patient with PatientID-{patientid} deleted!'.format(patientid=patientid),'category':'success'}
    return msg

def add_new_message(doctorid,patientid,message):
    results=db.get_user_for_userid(doctorid)
    if results[0]['userid']==doctorid:
        db.add_new_message(doctorid,patientid,message)
        msg={'msg':'Message sent succesfully!','category':'success'}
    else:
        msg={'msg':'Doctor not found!','category':'error'}
    return msg



