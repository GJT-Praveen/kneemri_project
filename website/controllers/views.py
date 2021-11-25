from flask import Blueprint, render_template, request, flash, make_response
from werkzeug.utils import redirect
# from werkzeug.utils import secure_filename
from website.controllers import db
from flask_login import current_user
from website import login_with_role
from website.models.patient_list import patient
from website.utils.controller_utils import add_patient_data,delete_patient_data,add_new_message
# from website.utils.forms import add_patient_form, delete_patient_form, download_report_form
# from website import scans
import pdfkit
import os
from website.ai_utils.predict import predict_diagnosis


config = pdfkit.configuration(
    wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html')


@views.route('/Dhome_Dashboard', methods=['GET', 'POST'])
@login_with_role('Doctor')
def Dhome_Dashboard():
    patients = db.get_patients_for_doctorid(current_user.userid)
    counts = db.get_data_for_doctorid(current_user.userid)[0]
    return render_template('Dhome_Dashboard.html', user=current_user, patients_table=patients[0:10], count1=counts['knees_cracked_count'], count2=counts['current_patients_count'], count3=counts['unread_messages_count'])


@views.route('/Dhome_messages')
@login_with_role('Doctor')
def Dhome_messages():
    return render_template('Dhome_messages.html')


@views.route('/Dhome_patients', methods=['GET', 'POST'])
@login_with_role('Doctor')
def Dhome_patients():
    patients = db.get_patients_for_doctorid(current_user.userid)
    return render_template('Dhome_patients.html', user=current_user, patients_table=patients)


@views.route('/Dhome_settings')
@login_with_role('Doctor')
def Dhome_settingss():
    return render_template('Dhome_settings.html', user=current_user)


@views.route('/Phome')
@login_with_role('Patient')
def Phome():
    patients= db.get_patients_for_patientid(current_user.userid)
    if patients:
        report_ready='Yes'
        abnormal=patients[0]['abnormal']
        acl=patients[0]['acl']
        meniscus=patients[0]['meniscus']
        return render_template('Phome_base.html', user=current_user, report_ready=report_ready,abnormal=abnormal,acl=acl,meniscus=meniscus)
    else:
        report_ready='No'
        return render_template('/Phome_base.html',user=current_user, report_ready=report_ready)
    


@views.route('/generate_pdf', methods=['POST'])
@login_with_role(['Doctor', 'Patient'])
def generate_pdf():
    print(request.form)
    if request.method == 'POST':
        patientid = request.form.get('patientid')
        name = request.form.get('name')
        email = request.form.get('email')
        pnumber = request.form.get('pnumber')
        gender = request.form.get('gender')
        abnormal = request.form.get('abnormal')
        acl = request.form.get('acl')
        meniscus = request.form.get('meniscus')
        rendered = render_template('pdf_template.html', patientid=patientid, name=name, email=email,
                                   pnumber=pnumber, gender=gender, abnormal=abnormal, acl=acl, meniscus=meniscus)
        pdf = pdfkit.from_string(rendered, False, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename={patientid}.pdf'.format(
            patientid=patientid)
        return response

@views.route('/add_patient',methods=['POST','GET'])
@login_with_role('Doctor')
def add_patient_request():
    print(request.form)
    if request.method=='POST':
        upload_dir = r'website\ai_utils\uploads'
        doctorid = request.form.get('doctorid')
        name = request.form.get('name')
        patientid = request.form.get('patientid')
        email = request.form.get('email')
        pnumber = request.form.get('pnumber')
        gender = request.form.get('gender')
        axi_scan = request.files['axi_scan']
        cor_scan = request.files['cor_scan']
        sag_scan = request.files['sag_scan']

        if axi_scan and cor_scan and sag_scan:    
            axi_scan.save(os.path.join(upload_dir,'axi_scan.npy'))
            cor_scan.save(os.path.join(upload_dir,'cor_scan.npy'))
            sag_scan.save(os.path.join(upload_dir,'sag_scan.npy'))
            
        else:
            msg={'msg':'Please upload all scans','category':'error'}
            flash(msg['msg'], msg['category'])
            return redirect('/Dhome_Dashboard')

        abnormal,acl,meniscus=predict_diagnosis()

        os.remove(os.path.join(upload_dir,'axi_scan.npy'))
        os.remove(os.path.join(upload_dir,'cor_scan.npy'))
        os.remove(os.path.join(upload_dir,'sag_scan.npy'))

        msg = add_patient_data(patientid, doctorid, name, email,
                      pnumber, gender, abnormal, acl, meniscus)

        flash(msg['msg'], msg['category'])
        return redirect('/Dhome_Dashboard')

@views.route('/delete_patient', methods=['POST'])
@login_with_role('Doctor')
def delete_patient():
    if request.method=='POST':
        location=request.form.get('location')
        patientid = request.form.get('patientid')
        msg = delete_patient_data(current_user.userid, patientid)
        flash(msg['msg'],msg['category'])
        if location=='patients':
            return redirect('/Dhome_patients')
        return redirect('/Dhome_Dashboard')

@views.route('/submit_patient_generate_pdf',methods=['POST'])
@login_with_role('Patient')
def submit_scan_generate_pdf():
    print(request.form)
    if request.method=='POST':
        upload_dir = r'website\ai_utils\uploads'
        name = request.form.get('name')
        patientid = request.form.get('patientid')
        email = request.form.get('email')
        pnumber = request.form.get('pnumber')
        gender = request.form.get('gender')
        axi_scan = request.files['axi_scan']
        cor_scan = request.files['cor_scan']
        sag_scan = request.files['sag_scan']

        if axi_scan and cor_scan and sag_scan:    
            axi_scan.save(os.path.join(upload_dir,'axi_scan.npy'))
            cor_scan.save(os.path.join(upload_dir,'cor_scan.npy'))
            sag_scan.save(os.path.join(upload_dir,'sag_scan.npy'))
            
        else:
            msg={'msg':'Please upload all scans','category':'error'}
            flash(msg['msg'], msg['category'])
            return redirect('/Phome')

        abnormal,acl,meniscus=predict_diagnosis()

        os.remove(os.path.join(upload_dir,'axi_scan.npy'))
        os.remove(os.path.join(upload_dir,'cor_scan.npy'))
        os.remove(os.path.join(upload_dir,'sag_scan.npy'))

        rendered = render_template('pdf_template.html', patientid=patientid, name=name, email=email,
                                   pnumber=pnumber, gender=gender, abnormal=abnormal, acl=acl, meniscus=meniscus)

        pdf = pdfkit.from_string(rendered, False, configuration=config)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename={patientid}.pdf'.format(
            patientid=patientid)
        return response

@views.route('/send_message',methods=['POST'])
@login_with_role('Patient')
def send_message():
    print(request.form)
    if request.method=='POST':
        patientid=request.form.get('patientid')
        doctorid=request.form.get('doctorid')
        message=request.form.get('message')
        msg= add_new_message(doctorid,patientid,message)
        flash(msg['msg'],msg['category'])
    return redirect('/Phome')