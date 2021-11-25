from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory
from cassandra import Unauthorized, Unavailable, AuthenticationFailed, OperationTimedOut, ReadTimeout

class SessionManager(object):

    __instance = None
    username = None
    password = None
    keyspace = None
    secure_connect_bundle_path = None
    initialized = False
    _session = None

    # ping_query = "SELECT data_center FROM system.local"

    @staticmethod
    def get_instance():
        if SessionManager.__instance is None:
            SessionManager()
        return SessionManager.__instance

    def __init__(self):
        SessionManager.__instance = self

    def save_credentials(self, username, password, keyspace, secure_connection_bundle_path):
        self.username = username
        self.password = password
        self.keyspace = keyspace
        self.secure_connect_bundle_path = secure_connection_bundle_path
        self.initialized = True


    def connect(self):
        if self.initialized is False:
            raise Exception('Please initialize the connection parameters first with SessionManager.save_credentials')

        if self._session is None:
            # This is how you use the Astra secure connect bundle to connect to an Astra database
            # note that the database username and password required.
            # note that no contact points or any other driver customization is required.
            astra_config = {
                'secure_connect_bundle': self.secure_connect_bundle_path
            }

            cluster = Cluster(cloud=astra_config, auth_provider=PlainTextAuthProvider(self.username, self.password))
            self._session = cluster.connect(keyspace=self.keyspace)

            # have the driver return results as dict
            self._session.row_factory = dict_factory

        return self._session

