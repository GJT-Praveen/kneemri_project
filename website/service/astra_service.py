from website.dao.session_manager import SessionManager
from website.dao.users_list_dao import user_list_DAO
from website.dao.patient_list_dao import patient_list_DAO
from website.dao.doctors_data_dao import doctors_data_DAO
from website.dao.messages_to_doctors_dao import messages_to_doctor_DAO

class db_service(object):

    users_dao = None
    patient_list_dao = None
    doctor_data_dao = None
    messages_to_doctor_dao = None
    _session_manager = SessionManager()
    _session = None

    def get_session(self):
        if self._session is None:
            self._session = self._session_manager.get_instance().connect()

        return self._session

    def save_credentials(self, username, password, keyspace, secure_connect_bundle_path):
        self._session_manager.save_credentials(username, password, keyspace, secure_connect_bundle_path)

    def connect(self):
        return self._session_manager.connect()

    def get_Users_dao(self):
        if self.users_dao is None:
            self.users_dao = user_list_DAO(self.get_session())

        return self.users_dao
    
    def get_patient_list_dao(self):
        if self.patient_list_dao is None:
            self.patient_list_dao = patient_list_DAO(self.get_session())
        return self.patient_list_dao

    def get_doctors_data_dao(self):
        if self.doctor_data_dao is None:
            self.doctor_data_dao = doctors_data_DAO(self.get_session())
        
        return self.doctor_data_dao

    def get_messages_to_doctor_dao(self):
        if self.messages_to_doctor_dao is None:
            self.messages_to_doctor_dao = messages_to_doctor_DAO(self.get_session())
        return self.messages_to_doctor_dao

    def create_new_user(self, name, userid, email, pnumber, password, gender, usertype):
        if usertype == 'Doctor':
            print(self.get_doctors_data_dao())
            self.get_doctors_data_dao().write_doctor_data(userid,knees_cracked_count=0,current_patients_count=0,unread_messages_count=0)
        return self.get_Users_dao().write_user(name, userid, email, pnumber, password, gender, usertype)

    def get_user_for_userid(self, userid):
            result = self.get_Users_dao().get_user_for_userid(userid)
            if result:
                return result
            else:
                result=[{'userid':'9999','name':'Admin','email':'admin@admin.com','pnumber':'9705876870','password':'admin','gender':'Male','usertype':'Admin'}]
                return result

    def get_user_for_email(self, email):
        return self.get_Users_dao().get_user_for_email(email)
    
    def add_new_patient(self, patientid, doctorid, name, email, pnumber, gender,abnormal,acl,meniscus):
        self.update_knees_cracked_count(doctorid)
        self.update_current_patients_count(doctorid,"new")
        return self.get_patient_list_dao().write_patient(patientid, doctorid, name, email, pnumber, gender,abnormal, acl, meniscus)
    
    def get_patients_for_doctorid(self, doctorid):
        return self.get_patient_list_dao().get_patients_for_doctorid(doctorid)

    def get_patients_for_patientid(self,patientid):
        return self.get_patient_list_dao().get_patients_for_patientid(patientid)
    
    def delete_patient(self, doctorid, patientid):
        self.update_current_patients_count(doctorid,"delete")
        return self.get_patient_list_dao().delete_patient(patientid)

    def get_data_for_doctorid(self, doctorid):
        return self.get_doctors_data_dao().get_data_for_doctorid(doctorid)

    def update_knees_cracked_count(self, doctorid):
        return self.get_doctors_data_dao().update_knees_cracked_count(doctorid)
    
    def update_current_patients_count(self, doctorid, operation):
        return self.get_doctors_data_dao().update_current_patients_count(doctorid,operation)

    def update_unread_messages_count(self, doctorid):
        unread_messages_count = self.get_unread_messages_count(doctorid)
        return self.get_doctors_data_dao().update_unread_messages_count(doctorid,unread_messages_count)

    def add_new_message(self, doctorid, patientid, message):
        return self.get_messages_to_doctor_dao().write_message(doctorid,patientid,message,read=False)
    
    def get_messages_for_doctorid(self, doctorid):
        return self.get_messages_to_doctor_dao().get_messages_for_doctorid(doctorid)
    
    def get_unread_messages_count(self,doctorid):
        return self.get_messages_to_doctor_dao().get_unread_messages_count(doctorid)
    
    def update_message_read(self, doctorid):
        return self.get_messages_to_doctor_dao().update_message_read(doctorid)

    # def delete_messages_from_patient(self,doctorid,patientid):
    #     return self.get_messages_to_doctor_dao().delete_message(doctorid,patientid)
    
