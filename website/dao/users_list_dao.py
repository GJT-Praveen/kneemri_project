from website.utils.cql_util_file import get_cql_schema_string_from_file

from website.models.user_list import User


# Data Access Object for the spacecraft_journey_catalog database table
# Contains CQL Statements and DataStax Driver APIs for reading and writing from the database
class user_list_DAO(object):

    table_name = "Users"
    keyspace="kneemri"
    create_stmt = get_cql_schema_string_from_file(table_name)
    create_index_email_for_Users = "CREATE INDEX IF NOT EXISTS email on {keyspace}.{table_name}(email);".format(keyspace=keyspace, table_name=table_name)

    insert_stmt = 'INSERT INTO {table_name} (name, userid, email, pnumber, password, gender, usertype) ' \
                  'VALUES (:name,:userid,:email,:pnumber,:password,:gender, :usertype);'.format(table_name=table_name)

    select_user_for_userid_stmt = 'SELECT * FROM {table_name} WHERE userid = :userid;' \
                                              ''.format(table_name=table_name)

    select_user_for_email_stmt = 'SELECT * FROM {table_name} ' \
                                                'WHERE email = :email;' \
                                                ''.format(table_name=table_name)
    

    def __init__(self, _session):
        self._session = _session
        self.maybe_create_schema()
        self.insert_prep_stmt = _session.prepare(self.insert_stmt)
        self.select_user_for_userid_prep_stmt = _session.prepare(self.select_user_for_userid_stmt)
        self.select_user_for_email_prep_stmt = _session.prepare(self.select_user_for_email_stmt)

    def maybe_create_schema(self):
        self._session.execute(self.create_stmt)
        self._session.execute(self.create_index_email_for_Users)

    def write_user(self, name, userid, email, pnumber, password, gender, usertype):
        # We use the DataStax Driver's Async API here to write the rows to the database in a non-blocking fashion

        def handle_success(results):
            pass

        def handle_error(exception):
            raise Exception('Failed to write row: ' + exception)

        this_user = User( name, userid, email, pnumber, password, gender, usertype)

        insert_future = self._session.execute_async(self.insert_prep_stmt.bind({
            'name': this_user.name,
            'userid': this_user.userid,
            'email': this_user.email,
            'pnumber': this_user.pnumber,
            'password': this_user.password,
            'gender': this_user.gender,
            'usertype': this_user.usertype, }
        ))

        insert_future.add_callbacks(handle_success, handle_error)

    def get_user_for_userid(self, userid):
        
        result = self._session.execute(self.select_user_for_userid_prep_stmt.bind({
            'userid': userid}
        ))
        return result

    def get_user_for_email(self, email):
        result = self._session.execute(self.select_user_for_email_prep_stmt.bind({
            'email': email,}
        ))
        return result

    def get_password_for_userid(self, userid):
        result = self._session.execute(self.select_user_for_userid_prep_stmt.bind({
            'userid':userid}
            ))
        return result[0]['password']

    def get_usertype_for_userid(self, userid):
        result = self._session.execute(self.select_user_for_userid_prep_stmt.bind({
            'userid':userid}
            ))
        return result[0]['usertype']