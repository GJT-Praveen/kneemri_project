from website.utils.cql_util_file import get_cql_schema_string_from_file
from website.models.messages_to_doctors import Message

class messages_to_doctor_DAO(object):

    keyspace='kneemri'
    table_name = 'messages_to_doctors'

    create_stmt=get_cql_schema_string_from_file(table_name)
    
    create_index_for_patientid_stmt = 'CREATE INDEX IF NOT EXISTS patientid on {keyspace}.{table_name}(patientid)'\
                                                ''.format(keyspace=keyspace, table_name=table_name)
    create_index_for_read_stmt = 'CREATE INDEX IF NOT EXISTS read on {keyspace}.{table_name}(read)'\
                                                ''.format(keyspace=keyspace, table_name=table_name)
    insert_stmt =  'INSERT INTO {table_name} (doctorid, patientid, message, read) ' \
                  'VALUES (:doctorid, :patientid, :message, :read);'.format(table_name=table_name)
    # delete_stmt = 'DELETE FROM {table_name} WHERE doctorid=:doctorid AND patientid= :patientid;'\
    #                                             ''.format(table_name=table_name)
    select_messages_for_doctorid_stmt = 'SELECT * FROM {table_name} WHERE doctorid = :doctorid;' \
                                                ''.format(table_name=table_name)
    select_unread_messages_for_doctorid_stmt = 'SELECT * FROM {table_name} WHERE doctorid = :doctorid AND read= False;' \
                                                ''.format(table_name=table_name)
    updata_message_read_stmt = 'UPDATE {table_name} SET read = True WHERE doctorid = :doctorid;'\
                                                ''.format(table_name=table_name)
    
    
    def __init__(self, _session):
        self._session = _session
        self.maybe_create_schema()
        self.insert_prep_stmt = _session.prepare(self.insert_stmt)
        self.select_messages_for_doctorid_prep_stmt = _session.prepare(self.select_messages_for_doctorid_stmt)
        self.select_unread_messages_for_doctorid_prep_stmt = _session.prepare(self.select_unread_messages_for_doctorid_stmt)
        self.update_message_read_prep_stmt = _session.prepare(self.updata_message_read_stmt)
        # self.delete_prep_stmt =_session.prepare(self.delete_stmt)
    
    def maybe_create_schema(self):
        self._session.execute(self.create_stmt)
        self._session.execute(self.create_index_for_read_stmt)
        self._session.execute(self.create_index_for_patientid_stmt)
    
    def write_message(self, doctorid, patientid, message, read):
        # We use the DataStax Driver's Async API here to write the rows to the database in a non-blocking fashion

        def handle_success():
            pass

        def handle_error(exception):
            raise Exception('Failed to write row: ' + exception)

        this_patient = Message(patientid,doctorid,message,read)

        insert_future = self._session.execute_async(self.insert_prep_stmt.bind({
            
            'doctorid': this_patient.doctorid,
            'patientid': this_patient.patientid,
            'message': this_patient.message,
            'read': this_patient.read}
        ))

        insert_future.add_callbacks(handle_success, handle_error)

    def get_unread_messages_count(self,doctorid):
        result = self._session.execute(self.select_unread_messages_for_doctorid_prep_stmt.bind({
            'doctorid': doctorid
        }))
        return len(result)
        
    def update_message_read(self, doctorid):
        self._session.execute(self.update_message_read_prep_stmt)

    def get_messages_for_doctorid(self, doctorid):
        result = self._session.execute(self.select_messages_for_doctorid_prep_stmt.bind({
            'doctorid': doctorid}
        ))
        return result

    # def delete_message(self,doctorid,patientid):
    #     self._session.execute(self.delete_prep_stmt.bind({
    #         'doctorid' :doctorid,
    #         'patientid': patientid}
    #     ))
