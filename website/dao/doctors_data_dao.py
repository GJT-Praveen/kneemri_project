from website.utils.cql_util_file import get_cql_schema_string_from_file
from website.models.doctors_data import doctor

class doctors_data_DAO(object):
    table_name = "doctors_data"
    knees_cracked_count=0
    current_patients_count=0
    

    create_stmt = get_cql_schema_string_from_file(table_name)

    insert_stmt =  'INSERT INTO {table_name} (doctorid, knees_cracked_count, current_patients_count, unread_messages_count) ' \
                  'VALUES (:doctorid, :knees_cracked_count, :current_patients_count, :unread_messages_count );'.format(table_name=table_name)
    
    select_data_for_doctorid_stmt = 'SELECT * FROM {table_name} WHERE doctorid = :doctorid;' \
                                                ''.format(table_name=table_name)

    update_knees_cracked_count_stmt = 'UPDATE {table_name} SET knees_cracked_count= :knees_cracked_count WHERE doctorid = :doctorid;'\
                                                ''.format(table_name=table_name)

    update_unread_messages_count_stmt = 'UPDATE {table_name} SET unread_messages_count= :unread_messages_count WHERE doctorid = :doctorid;'\
                                                ''.format(table_name=table_name) 

    update_current_patients_count_stmt = 'UPDATE {table_name} SET current_patients_count= :current_patients_count WHERE doctorid = :doctorid;'\
                                                ''.format(table_name=table_name)



    def __init__(self, _session):
        self._session = _session
        self.maybe_create_schema()
        self.insert_prep_stmt = _session.prepare(self.insert_stmt)
        self.select_data_for_doctorid_prep_stmt = _session.prepare(self.select_data_for_doctorid_stmt)
        self.update_knees_cracked_count_prep_stmt = _session.prepare(self.update_knees_cracked_count_stmt)
        self.update_unread_messages_count_prep_stmt = _session.prepare(self.update_unread_messages_count_stmt)
        self.update_current_patients_count_prep_stmt = _session.prepare(self.update_current_patients_count_stmt)

    def maybe_create_schema(self):
        self._session.execute(self.create_stmt)
    
    def write_doctor_data(self, doctorid, knees_cracked_count, current_patients_count, unread_messages_count):
        # We use the DataStax Driver's Async API here to write the rows to the database in a non-blocking fashion

        def handle_success():
            pass

        def handle_error(exception):
            raise Exception('Failed to write row: ' + exception)

        this_data = doctor(doctorid, knees_cracked_count, current_patients_count, unread_messages_count)

        insert_future = self._session.execute_async(self.insert_prep_stmt.bind({
            
            'doctorid': this_data.doctorid,
            'knees_cracked_count' : this_data.knees_cracked_count,
            'current_patients_count': this_data.current_patients_count,
            'unread_messages_count': this_data.unread_messages_count,}
        ))

        insert_future.add_callbacks(handle_success, handle_error)

    def get_data_for_doctorid(self, doctorid):
        result = self._session.execute(self.select_data_for_doctorid_prep_stmt.bind({
            'doctorid': doctorid}
        ))
        return result

    def update_knees_cracked_count(self, doctorid):
        result = self.get_data_for_doctorid(doctorid)
        knees_cracked_count= result[0]['knees_cracked_count']+1

        self._session.execute(self.update_knees_cracked_count_prep_stmt.bind({
            'doctorid': doctorid,
            'knees_cracked_count': knees_cracked_count,}
        ))
    
    def update_current_patients_count(self, doctorid, operation):
        result = self.get_data_for_doctorid(doctorid)
        if operation=='new':
            current_patients_count = result[0]['current_patients_count']+1
        if operation=='delete':
            current_patients_count = result[0]['current_patients_count']-1
        self._session.execute(self.update_current_patients_count_prep_stmt.bind({
            'doctorid': doctorid,
            'current_patients_count': current_patients_count,}
        ))
    def update_unread_messages_count(self, doctorid, unread_messages_count):
        self._session.execute(self.update_unread_messages_count_prep_stmt.bind({
            'doctorid': doctorid,
            'unread_messages_count': unread_messages_count}
        ))
