CREATE TABLE IF NOT EXISTS Users (
    userid text,
    name text,
    email text,
    pnumber text,
    password text,
    gender text,
    usertype text,
    PRIMARY KEY (userid)
)
;

CREATE TABLE IF NOT EXISTS patient_list (
    patientid text,
    doctorid text,
    name text,
    email text,
    pnumber text,
    gender text,
    abnormal text,
    acl text,
    meniscus text,
    PRIMARY KEY (patientid)
)
;

CREATE TABLE IF NOT EXISTS doctors_data (
    doctorid text,
    knees_cracked_count int,
    current_patients_count int,
    unread_messages_count int,
    PRIMARY KEY (doctorid)
)
;

CREATE TABLE IF NOT EXISTS messages_to_doctors (
    doctorid text,
    patientid text,
    message text,
    read boolean,
    PRIMARY KEY (doctorid)
)
;





