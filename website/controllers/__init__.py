import os 
from website.service.astra_service import db_service



client_id = 'GYjWlzmHorGknuFHcyhMaJeZ'
client_secret_key = "ITwzx5n_P1WXBkI-s+MLZmQ9CJouzSPccNgqIknTfmuWdaC6nRWhcG-3oKy9YAIKXcmvgcDGYZ,g2097+bAwqaL.EgiyA9J2LQOCtg-Fa7uUIshL-gP0S4XX8ruRslHU"
keyspace = 'kneemri'
bundle_path = os.path.abspath('website/static/secure-connect-kneemri.zip')

db = db_service()
db.save_credentials(client_id,client_secret_key,keyspace,bundle_path)

