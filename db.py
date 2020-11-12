import mysql.connector
import json
import time
import numpy as np

from server import app


def __createConnection(buffered=False):
    connection = mysql.connector.connect(**app.config['DB'])
    return connection, connection.cursor(buffered=buffered) 

def __closeConnection(connection, cursor):
    cursor.close()
    connection.close()

def __renewCursor(connection, cursor, buffered=False):
    # Returns new cursor
    cursor.close()
    return connection.cursor(buffered=buffered)

# Wait for mysql connection
def waitForConnection():
    print(">> Waiting for MySQL connection...")
    count = 0
    while count == 0:
        time.sleep(1)
        try:
            connection, cursor = __createConnection(buffered=True)
            cursor.execute('SELECT count(*) FROM information_schema.TABLES WHERE (TABLE_SCHEMA = \'smart_tafel\') AND (TABLE_NAME = \'scan\')')
            connection.commit()
            count = cursor.fetchone()[0]
            __closeConnection(connection, cursor)
        except:
            pass
    print(">> Established MySQL connection")

# Create new row for scan
def insertScan(lang, name, email, phone, date, bedrijf, teelt, fotographer, desc):
    connection, cursor = __createConnection()

    # if email is not None and phone is None:
    #     cursor.execute('INSERT INTO scan (`language`, `name`, `email`) VALUES (%s, %s, %s)', (lang, name, email))
    # elif email is None and phone is not None:
    #     cursor.execute('INSERT INTO scan (`language`, `name`, `phone`) VALUES (%s, %s, %s)', (lang, name, phone))
    # else:
    cursor.execute('INSERT INTO scan (`language`, `name`, `email`, `phone`, `date`, `bedrijf`, `teelt`, `phone`, `desc`) VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s)', (lang, name, email, phone, date, bedrijf, teelt, fotographer, desc))
    
    connection.commit()

    cursor = __renewCursor(connection, cursor, buffered=True)

    cursor.execute('SELECT LAST_INSERT_ID()')
    connection.commit()

    id = cursor.fetchone()[0]

    __closeConnection(connection, cursor)
    return id

# Get oldest scan where audio can be added
def getScanReadyAudio():
    connection, cursor = __createConnection(buffered=True)

    cursor.execute('SELECT `id`, `language` FROM scan WHERE `state` = \'ready_audio\' ORDER BY timestamp ASC LIMIT 1')
    connection.commit()

    id = None
    lang = None
    if cursor.rowcount == 1:
        id, lang = cursor.fetchone()

    __closeConnection(connection, cursor)
    return id, lang

# Get oldest scan where location can be added
def getScanReadyLoc():
    connection, cursor = __createConnection(buffered=True)

    cursor.execute('SELECT `id`, `language` FROM scan WHERE `state` = \'ready_loc\' ORDER BY `timestamp` ASC LIMIT 1')
    connection.commit()

    id = None
    lang = None
    if cursor.rowcount == 1:
        id, lang = cursor.fetchone()

    __closeConnection(connection, cursor)
    return id, lang


def checkScanId(id):
    connection, cursor = __createConnection(buffered=True)

    cursor.execute('SELECT `id` FROM scan WHERE `id` = %s', (id,))
    connection.commit()

    id = None
    if cursor.rowcount == 1:
        id = cursor.fetchone()[0]

    __closeConnection(connection, cursor)
    return id


def getScanState(id):
    connection, cursor = __createConnection(buffered=True)

    cursor.execute('SELECT `state` FROM scan WHERE `id` = %s', (id,))
    connection.commit()

    state = None
    if cursor.rowcount == 1:
        state = cursor.fetchone()[0]

    __closeConnection(connection, cursor)
    return state


def updateScanState(id, state):
    if state in ['ready_audio', 'ready_loc', 'done', 'canceled']:
        connection, cursor = __createConnection()

        cursor.execute('UPDATE scan SET `state` = %s WHERE `id` = %s', (state, id))
        connection.commit()

        __closeConnection(connection, cursor)
        return id

    return None


def updateScanAudio(id, audio):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `audio` = %s WHERE `id` = %s', (1 if audio else 0, id))
    connection.commit()
    
    __closeConnection(connection, cursor)


def updateScanLoc(id, lat, lng):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `location` = POINT(%s, %s) WHERE `id` = %s', (lat, lng, id))
    connection.commit()

    __closeConnection(connection, cursor)


def getScanLoc(id):
    connection, cursor = __createConnection(buffered=True)

    cursor.execute('SELECT ST_X(`location`), ST_Y(`location`) FROM scan WHERE `id` = %s', (id,))
    connection.commit()

    location = None
    if cursor.rowcount == 1:
        location = cursor.fetchone()

    __closeConnection(connection, cursor)
    return location


def updateScanAesScore(id, aes_score):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `aes_score` = %s WHERE `id` = %s', (aes_score, id))
    connection.commit()

    __closeConnection(connection, cursor)


def getScansLoc():
    connection, cursor = __createConnection()

    cursor.execute('SELECT `id`, ST_X(`location`), ST_Y(`location`) FROM scan WHERE `state` = \'done\'')

    data = cursor.fetchall()

    __closeConnection(connection, cursor)
    return data
    

def getScansTopAesToday(limit):
    connection, cursor = __createConnection()

    cursor.execute('SELECT `id`, `aes_score` FROM scan WHERE `state` = \'done\' AND `aes_score` IS NOT NULL ORDER BY `aes_score` DESC LIMIT %s', (limit,))

    data = cursor.fetchall()

    __closeConnection(connection, cursor)
    return data


def getScansTopTotalToday(limit):
    connection, cursor = __createConnection()

    cursor.execute('SELECT `id`, `total_score` FROM scan WHERE `state` = \'done\' AND `total_score` IS NOT NULL AND DATE(`timestamp`) = CURDATE() ORDER BY `total_score` DESC LIMIT %s', (limit,))
    data = cursor.fetchall()

    __closeConnection(connection, cursor)
    return data


def getScansDoneTopTotalYesterday(limit):
    connection, cursor = __createConnection()

    cursor.execute('SELECT `id`, `total_score` FROM scan WHERE `state` = \'done\' AND `total_score` IS NOT NULL ORDER BY `total_score` DESC LIMIT %s', (limit,))
    data = cursor.fetchall()

    __closeConnection(connection, cursor)
    return data


def updateScanVector(id, vector):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `vector` = %s WHERE `id` = %s', (json.dumps(vector, separators=(',', ':')), id))
    connection.commit()

    __closeConnection(connection, cursor)


def getScanVector(id):
    connection, cursor = __createConnection(buffered=True)

    cursor.execute('SELECT `vector` FROM scan WHERE `id` = %s', (id,))
    connection.commit()

    vector = None
    if cursor.rowcount == 1:
        vector = json.loads(cursor.fetchone()[0])

    __closeConnection(connection, cursor)
    return vector


def updateScanSimScore(id, sim_score):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `sim_score` = %s WHERE `id` = %s', (sim_score, id))
    connection.commit()

    __closeConnection(connection, cursor)


def updateScanLocScore(id, loc_score):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `loc_score` = %s WHERE `id` = %s', (loc_score, id))
    connection.commit()

    __closeConnection(connection, cursor)


def updateScanTotalScore(id, total_score):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `total_score` = %s WHERE `id` = %s', (total_score, id))
    connection.commit()

    __closeConnection(connection, cursor)


def getScansVectorPrevDay():
    connection, cursor = __createConnection()

    cursor.execute('SELECT `id`, `vector` FROM scan WHERE `vector` IS NOT NULL AND DATE(`timestamp`) = SUBDATE(CURDATE(),1)')
    data = cursor.fetchall()

    data_return = []
    for i in range(len(data)):
        data_return.append([data[i][0], np.asarray(json.loads(data[i][1]))])

    __closeConnection(connection, cursor)
    return np.asarray(data_return)


def getScansLocPrevDay():
    connection, cursor = __createConnection()

    cursor.execute('SELECT `id`, ST_X(`location`), ST_Y(`location`) FROM scan WHERE `location` IS NOT NULL AND DATE(`timestamp`) = SUBDATE(CURDATE(),1)')
    data = cursor.fetchall()

    data_return = []
    for i in range(len(data)):
        data_return.append([data[i][0], [data[i][1], data[i][2]]])

    __closeConnection(connection, cursor)
    return np.asarray(data_return)


def getScansLocVectorAesScorePrevDay():
    connection, cursor = __createConnection()

    cursor.execute('SELECT `id`, ST_X(`location`), ST_Y(`location`), `vector`, `aes_score` FROM scan WHERE `location` IS NOT NULL AND `vector` IS NOT NULL AND `aes_score` IS NOT NULL AND DATE(`timestamp`) = SUBDATE(CURDATE(),1)')
    data = cursor.fetchall()

    data_return = []
    for i in range(len(data)):
        data_return.append([data[i][0], [data[i][1], data[i][2]], np.asarray(json.loads(data[i][3])), data[i][4]])

    __closeConnection(connection, cursor)
    return np.asarray(data_return)


def getScanAesSimLocScore(id):
    connection, cursor = __createConnection(buffered=True)

    cursor.execute('SELECT `aes_score`, `sim_score`, `loc_score` FROM scan WHERE `id` = %s', (id,))
    connection.commit()

    scores = None, None, None
    if cursor.rowcount == 1:
        scores = cursor.fetchone()

    __closeConnection(connection, cursor)
    return scores


def updateScanSimLocTotalScore(id, sim_score, loc_score, total_score):
    connection, cursor = __createConnection()

    cursor.execute('UPDATE scan SET `sim_score` = %s, `loc_score` = %s, `total_score` = %s WHERE `id` = %s', (sim_score, loc_score, total_score, id))
    connection.commit()

    __closeConnection(connection, cursor)
