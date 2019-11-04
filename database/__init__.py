from database.sqlserverconn import SQLServerDBConn


def get_cols(cursor):
    return [c[0] for c in cursor.description]


def parse_result_set(cursor) -> list:
    cols = get_cols(cursor)
    row = cursor.fetchone()
    result = []
    while row:
        r = {
            c: row[i]
            for i, c in enumerate(cols)
        }
        result.append(r)
        row = cursor.fetchone()
    return result


def parse_procedure_result(cursor) -> dict:
    cols = ('status', 'errorMsg')
    row = cursor.fetchone()
    result = {
        c: row[i]
        for i, c in enumerate(cols)
    }
    return result


def sql_server_call_proc(spcall: str) -> dict:
    with SQLServerDBConn() as cnxn:
        cursor = cnxn.cursor()
        cursor.execute(spcall)
        result = parse_procedure_result(cursor)
        if result['status']:
            cursor.commit()
        else:
            cursor.rollback()
        cursor.close()
    return result


def sql_server_execute_query(query: str) -> list:
    with SQLServerDBConn() as cnxn:
        cursor = cnxn.cursor()
        cursor.execute(query)
        result = parse_result_set(cursor)
        cursor.close()
    return result
