from website.utils.cql_util_file import get_cql_schema_string_from_file
from website.models.patient_list import patient

class patient_list_DAO(object):
    table_name = 'patient_list'

    keyspace = 'kneemri'

    create_stmt = get_cql_schema_string_from_file(table_name)

    create_index_doctorid_stmt = 'CREATE INDEX IF NOT EXISTS doctorid on {keyspace}.{table_name}(doctorid);'\
                                                ''.format(keyspace=keyspace ,table_name=table_name)

    insert_stmt =  'INSERT INTO {table_name} (patientid, doctorid, name, email, pnumber, gender, abnormal, acl, meniscus) ' \
                  'VALUES (:patientid, :doctorid, :name, :email, :pnumber, :gender, :abnormal, : acl, :meniscus);'.format(table_name=table_name)

    delete_stmt = 'DELETE FROM {table_name} WHERE patientid= :patientid;'\
                                                ''.format(table_name=table_name)

    select_patients_for_doctorid_stmt = 'SELECT * FROM {table_name} WHERE doctorid = :doctorid;' \
                                              ''.format(table_name=table_name)
    select_patients_for_patientid_stmt = 'SELECT * FROM {table_name} WHERE patientid= :patientid'\
                                              ''.format(table_name=table_name)


    def __init__(self, _session):
        self._session = _session
        self.maybe_create_schema()
        self.insert_prep_stmt = _session.prepare(self.insert_stmt)
        self.select_patients_for_doctorid_prep_stmt = _session.prepare(self.select_patients_for_doctorid_stmt)
        self.select_patients_for_patientid_prep_stmt= _session.prepare(self.select_patients_for_patientid_stmt)
        self.delete_prep_stmt =_session.prepare(self.delete_stmt)
    
    def maybe_create_schema(self):
        self._session.execute(self.create_stmt)
        self._session.execute(self.create_index_doctorid_stmt)

    def write_patient(self, patientid, doctorid, name, email, pnumber, gender, abnormal, acl, meniscus):
        # We use the DataStax Driver's Async API here to write the rows to the database in a non-blocking fashion

        def handle_success():
            pass

        def handle_error(exception):
            raise Exception('Failed to write row: ' + exception)

        this_patient = patient(patientid, doctorid, name, email, pnumber, gender, abnormal, acl, meniscus)

        insert_future = self._session.execute_async(self.insert_prep_stmt.bind({
            
            'patientid': this_patient.patientid,
            'doctorid': this_patient.doctorid,
            'name': this_patient.name,
            'email': this_patient.email,
            'pnumber': this_patient.pnumber,
            'gender': this_patient.gender,
            'abnormal': this_patient.abnormal,
            'acl': this_patient.acl,
            'meniscus': this_patient.meniscus}
        ))

        insert_future.add_callbacks(handle_success, handle_error)
    
    def delete_patient(self, patientid):
        self._session.execute(self.delete_prep_stmt.bind({
            'patientid': patientid}
        ))
    
    def get_patients_for_doctorid(self, doctorid):
        result = self._session.execute(self.select_patients_for_doctorid_prep_stmt.bind({
            'doctorid': doctorid,}
        ))
        return result
    def get_patients_for_patientid(self,patientid):
        result = self._session.execute(self.select_patients_for_patientid_prep_stmt.bind({
            'patientid':patientid,}
            ))
        return result
    