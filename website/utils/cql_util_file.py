import os


# basic helper to get CQL schema from schema.cql file
def get_cql_schema_string_from_file(string_key):
    cql_string = ''
    start_of_block = False
    schema_cql_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'schema.cql')
    with open(schema_cql_file_path, 'r') as f:
        for line in f:
            # print("irerating now: "+line)
            if ' ' + string_key + ' ' in line:
                # print("passed condition1: "+line)
                cql_string += line.strip('\n').strip(' ')
                start_of_block = True

            if start_of_block is True and string_key not in line:
                # print('strip : '+line.strip('\n').strip(' '))
                cql_string += ' ' + line.strip('\n').strip(' ')

            if start_of_block ==True and ';' in line:
                # print('passed condition 3: '+line)
                break
        # print(cql_string)
    return cql_string