##
## =============================================
## ======== Sistema de Gestão de Dados =========
## ============== LECD  2024/2025 ==============
## =============================================
## =================== Demo ====================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors:
##   José D'Abruzzo Pereira <josep@dei.uc.pt>
##   Gonçalo Carvalho <gcarvalho@dei.uc.pt>
##   University of Coimbra


'''
How to run?
$ python3 -m venv cloud_query
$ source cloud_query/bin/activate
$ pip3 install flask
$ pip3 install jwt
$ pip3 install psycopg2-binary
$ python3 cloud_query.py
--> Ctrl+C to stop
$ deactivate
'''
import bcrypt
import jwt
from flask import Flask, jsonify, request
import logging
import psycopg2
import time
from datetime import datetime

app = Flask(__name__)
password_token = "cloud_query123"


def generate_token(user_id):
    payload = {
        'id': user_id,
        'exp': time.time() + 3600  # 1 hora de acesso por este token
    }
    token = jwt.encode(payload, password_token,
                       algorithm='HS256')  # HS256 (HMAC-SHA256) is a commonly used symmetric algorithm. It means the same secret key is used for both signing and verifying the token.
    return token


def verify_token():
    token = request.headers.get('Authorization')  # Temos de explicar isto
    if not token:
        return jsonify({'error': 'Token is missing'}), 401
    try:
        if token.startswith("Bearer "):
            token = token[7:]

        payload = jwt.decode(token, password_token, algorithms=["HS256"])

        if payload["exp"] < time.time():
            return jsonify({"message": "Token expirado!"}), 401

        return payload

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token expirado!"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Token inválido!"}), 401


def verify_admin():
    payload = verify_token()
    if isinstance(payload, tuple):
        return payload
    conn =db_connection()
    cur = conn.cursor()
    id_admin = payload['id']
    cur.execute("SELECT * FROM admin_ WHERE  user__id_user= %s", (id_admin,))
    row = cur.fetchone()

    if row:
        return payload
    else:
        return jsonify({"message": f"Acesso restrito a admistrador!"}), 403


def verify_crew():
    payload = verify_token()
    if isinstance(payload, tuple):
        return payload
    conn = db_connection()
    cur = conn.cursor()
    id = payload['id']
    cur.execute("SELECT * FROM crew_members WHERE  user__id_user= %s", (id,))
    row = cur.fetchone()

    if row:
        return payload
    else:
        return jsonify({"message": f"Acesso restrito a admistrador!"}), 403


def verify_passenger():
    payload = verify_token()
    if isinstance(payload, tuple):
        return payload
    conn = db_connection()
    cur = conn.cursor()
    id = payload['id']
    cur.execute("SELECT * FROM passanger WHERE  user__id_user= %s", (id,))
    row = cur.fetchone()

    if row:
        return payload
    else:
        return jsonify({"message": f"Acesso restrito a passageiro!"}), 403


def seat_generator(num_seats):
    # Seat creation considerations:
    # letters are COLUMS and numbers are ROWS
    # Display of a plane:
    """
    [1A,1B,3C,4D,5E
     2A,2B,3C,4D,5E
          ...
     nA,nB,nC,nD,nE]
    """
    # For simplification, we consider that every plane has 5 colums
    # and not every row is completed.

    num_colums = 5
    num_rows = num_seats // num_colums
    # Number of seats without a complete row
    num_seat_inc = num_seats % num_colums

    seats = []
    Alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'W', 'X', 'Y', 'Z']

    for i in range(num_rows):
        for lseat1 in range(num_colums):
            letter = Alphabet[lseat1]
            seats.append(str(i + 1) + letter)

    if num_seat_inc != 0:
        number = i + 2
        itr = 0
        while itr < num_seat_inc:
            letter = Alphabet[itr]
            seats.append(str(number) + letter)
            itr += 1

    return seats


@app.route('/cloud-query/')
def hello():
    return """

    Cloud Query!  <br/>
    <br/>
    Trabalho realizado por:<br/>
    Francisca<br/>
    Pedro <br/>
    Ramyad<br/>
    """


# verificado
def add_users():
    logger.info("###              DEMO: POST /users              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    # Verificação do input

    if len(payload) != 3:
        if "username" and "email" and "password" not in payload:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                  INSERT INTO user_ (username, email, password) 
                         VALUES ( %s,   %s ,   %s )"""
    has_password = bcrypt.hashpw(payload['password'].encode('utf-8'), bcrypt.gensalt())
    values = (payload['username'], payload['email'], has_password.decode('utf-8'))

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Inserted!'
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'
    finally:
        if conn is not None:
            conn.close()
    return jsonify(result)


# verificado
@app.route('/cloud-query/passenger', methods=['POST'])
def add_passenger():
    logger.info("###              DEMO: POST /passenger              ###")

    conn = db_connection()
    cur = conn.cursor()
    add_users()
    payload = request.get_json()
    logger.info("---- new passenger  ----")
    logger.debug(f'payload: {payload}')

    cur.execute("SELECT * FROM user_ where username = %s", (payload['username'],))
    rows = cur.fetchall()
    if len(rows) == 0:
        return jsonify({'status': 401, 'errors': 'Username does not exist!'}), 401

    row = rows[0]
    statement = """
                  INSERT INTO passanger (user__id_user) 
                          VALUES ( %s )"""
    values = (row[0],)
    try:
        cur.execute(statement, values)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': row[0]})


# verificado
@app.route('/cloud-query/admin', methods=['POST'])
def add_admin():
    logger.info("###              DEMO: POST /admin              ###");
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    add_users()
    payload = request.get_json()
    logger.info("---- new admin  ----")
    logger.debug(f'payload: {payload}')

    cur.execute("SELECT * FROM user_ where username = %s", (payload['username'],))
    rows = cur.fetchall()
    if len(rows) == 0:
        return jsonify({'status': 401, 'errors': 'Username does not exist!'}), 401

    row = rows[0]
    statement = """
                  INSERT INTO admin_ (user__id_user) 
                          VALUES ( %s )"""
    values = (row[0],)
    try:
        cur.execute(statement, values)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': row[0]})


'''{
    "username": "mario.geraldes.admin",
    "email": "mario.geraldes.admin@admin.pt",
    "password": "123adminmario",
    "role": "pilot",
    "crew_id": 1
}'''


# verificado
@app.route('/cloud-query/crew_member', methods=['POST'])
def add_crew_member():
    logger.info("###              DEMO: POST /crew_member              ###");
    payload_admin = verify_admin()
    if isinstance(payload_admin, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload_admin

    conn = db_connection()
    cur = conn.cursor()
    add_users()
    payload = request.get_json()
    logger.info("---- new crew_member  ----")
    logger.debug(f'payload: {payload}')

    cur.execute("SELECT * FROM user_ where username = %s", (payload['username'],))
    row = cur.fetchone()
    if len(row) == 0:
        return jsonify({'status': 401, 'errors': 'Username does not exist!'}), 401
    cur.execute("SELECT crew_id FROM crew where crew_id = %s", (payload['crew_id'],))
    crew_row = cur.fetchone()
    if crew_row:
        statement_1 = """
                          INSERT INTO crew_members (user__id_user,admin__user__id_user) 
                                  VALUES ( %s , %s)"""
        values_1 = (row[0], payload_admin['id'])
        if payload['role'] == 'pilot':
            statement_2 = """
            INSERT INTO pilot (crew_crew_id, crew_members_user__id_user) VALUES ( %s , %s)"""
            values_2 = (crew_row[0], row[0])
        elif payload['role'] == 'flight_attendante':
            statement_2 = """INSERT INTO flight_attendante (crew_crew_id, crew_members_user__id_user) VALUES ( %s , %s)"""
            values_2 = (payload['crew_id'], crew_row[0])

        try:
            cur.execute(statement_1, values_1)
            cur.execute(statement_2, values_2)
            cur.execute("commit")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
        finally:
            if conn is not None:
                conn.close()
        return jsonify({'status': 200, 'result': row[0]})
    else:
        return jsonify({'status': 401, 'errors': 'Crew id does not exist!'}), 401


# verificado
@app.route('/cloud-query/user', methods=['PUT'])
def login():
    logger.info("###              DEMO: PUT /users              ###")

    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()

    if len(payload) != 2:
        if "username" and "password" not in payload:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    username = payload.get('username')
    password = payload.get('password')

    cur.execute("SELECT * FROM user_ where username = %s", (username,))
    rows = cur.fetchall()

    if len(rows) == 0:
        return jsonify({'status': 401, 'errors': 'Username or password incorrect!'})

    row = rows[0]

    try:
        if bcrypt.checkpw(password.encode('utf-8'), row[3].encode('utf-8')):
            token = generate_token(row[0])
            return jsonify({'status': 200, 'result': token.decode('utf-8')}), 200
        else:
            return jsonify({'status': 401, 'errors': 'Username or password incorrect!'}), 401
    except ValueError:
        return jsonify({'status': 500, 'errors': 'Hash de senha inválido no banco de dados!'}), 500


# verificado
@app.route('/cloud-query/crew', methods=['POST'])
def add_crew():
    logger.info("###              DEMO: POST /crew              ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    logger.info("---- new crew  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                              INSERT INTO crew (admin__user__id_user) 
                                      VALUES ( %s )"""
    values = (payload['id'],)
    try:
        cur.execute(statement, values)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': 'Inserido com sucesso!'})


# verificado
@app.route('/cloud-query/crew', methods=['GET'])
def get_crews():
    logger.info("###              DEMO: GET /crew             ###")

    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM crew")
    rows = cur.fetchall()

    payload = []
    logger.debug("---- departments  ----")
    for row in rows:
        logger.debug(row)
        content = {'crew_id': int(row[0]), 'administrador_creater': row[1], 'crew_chief': row[2]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)


# verificado
@app.route('/cloud-query/airport', methods=['POST'])
def add_airport():
    logger.info("###              DEMO: POST /airport              ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    airport_json = request.get_json()

    # Verificar input

    if len(airport_json) != 3:
        if "city" and "name" and "country" not in airport_json:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    logger.info("---- new airport  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                                  INSERT INTO airport_ (admin__user__id_user, city,name, country) 
                                          VALUES ( %s,%s,%s,%s)"""
    values = (payload['id'], airport_json['city'], airport_json['name'], airport_json['country'])
    statement2 = """
    SELECT (airport_code) FROM airport_ WHERE  (city = %s AND name = %s AND country= %s )
    """
    values2 = (airport_json['city'], airport_json['name'], airport_json['country'])
    try:
        cur.execute(statement, values)
        cur.execute(statement2, values2)
        row = cur.fetchone()
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': row[0]})


# verificado
@app.route('/cloud-query/flight', methods=['POST'])
def add_flight():
    logger.info("###              DEMO: POST /flight             ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload
    conn = db_connection()
    cur = conn.cursor()
    flight_json = request.get_json()

    if len(flight_json) != 5:
        if "departure_time" and "arrival_time" and "existing_seats" and "airport_dep" and "airport_arr" not in flight_json:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    logger.info("---- new flight  ----")
    logger.debug(f'payload: {payload}')
    statement = """
                                      INSERT INTO flight_(departure_time,arrival_time,existing_seats,admin__user__id_user,airport_dep,airport_arr) 
                                      VALUES (%s, %s, %s, %s, %s, %s )
                                      """
    values = (datetime.strptime(flight_json['departure_time'], "%H:%M").time(),
              datetime.strptime(flight_json['arrival_time'], "%H:%M").time(), flight_json['existing_seats'],
              payload['id'], flight_json['airport_dep'], flight_json['airport_arr'])
    statement2 = """
        SELECT (flight_code) FROM flight_ WHERE departure_time=%s AND arrival_time=%s AND existing_seats=%s AND airport_dep=%s AND airport_arr=%s
        """
    values2 = (datetime.strptime(flight_json['departure_time'], "%H:%M").time(),
               datetime.strptime(flight_json['arrival_time'], "%H:%M").time(), flight_json['existing_seats'],
               flight_json['airport_dep'], flight_json['airport_arr'])
    try:
        cur.execute(statement, values)
        cur.execute(statement2, values2)
        rows = cur.fetchone()
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': rows[0]})


# verificado
@app.route('/cloud-query/schedule', methods=['POST'])
def add_schedule():
    logger.info("###              DEMO: POST /schedule             ###")
    payload = verify_admin()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    conn = db_connection()
    cur = conn.cursor()
    sch_json = request.get_json()
    logger.info("---- new schedule  ----")
    logger.debug(f'payload: {payload}')

    # Verificação do input

    if len(sch_json) != 4:
        if "flight_code" and "date" and "crew_id" and "ticket_price" not in sch_json:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    # Verificar se o voo existe

    statement = """
            SELECT 
                COUNT(*)
            FROM 
                flight_ f
            JOIN 
                schedule_ s ON fs.schedule__flight_date = s.flight_date
            WHERE 
                f.flight_code = %s
                AND
                f.flight_date = %s;"""

    values = (sch_json["flight_code"], sch_json["flight_date"],)

    cur.execute(statement, values)
    rows = cur.fetchone()

    if len(rows) != 1:
        return jsonify({'status': 500, 'errors': 'The flight does not exist!'}), 500

    sta = '''
    SELECT flight_date 
    FROM schedule_
    WHERE flight_date= %s
    '''

    values = (datetime.strptime(sch_json['date'], "%Y-%m-%d"),)
    cur.execute(sta, values)
    if cur.rowcount == 0:
        sta = '''
        INSERT INTO schedule_ (flight_date)
        VALUES (%s)
        '''
        data = datetime.strptime(sch_json['date'], "%Y-%m-%d").date()
        values = (data,)
        cur.execute(sta, values)

    sta = '''
    INSERT INTO  flight__schedule_(flight__flight_code, schedule__flight_date, crew_crew_id, ticket_price, admin__user__id_user) 
            VALUES (%s, %s, %s, %s, %s)
    '''
    val = (sch_json['flight_code'], datetime.strptime(sch_json['date'], "%Y-%m-%d"), sch_json['crew_id'],
           sch_json['ticket_price'], payload['id'])

    query_seats = '''
    SELECT existing_seats 
    FROM flight_
    WHERE flight_code= %s
    '''

    sta2 = '''
        INSERT INTO seat(available, seat_number, schedule__flight_date, flight__flight_code) 
        VALUES (%s,%s,%s,%s) 
    '''

    try:
        cur.execute(sta, val)
        cur.execute(query_seats, (sch_json['flight_code'],))
        seat_n = cur.fetchone()[0]
        for i in seat_generator(seat_n):
            val2 = (bool(True), i, data, sch_json['flight_code'])
            cur.execute(sta2, val2)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
    finally:
        if conn is not None:
            conn.close()
    return jsonify({'status': 200, 'result': 'Inserido com sucesso!'})


# QUERY 6 - verificada
@app.route('/cloud-query/check_routes', methods=['GET'])
def check_routes():
    logger.info("###              DEMO: GET /check_routes             ###");

    conn = db_connection()
    cur = conn.cursor()

    routes_payload = request.get_json()
    logger.info("----  Check the available routes ----")
    logger.debug(f'payload: {routes_payload}')


    # Caso onde não temos parametros de entrada
    if not routes_payload:
        statement = """
            SELECT 
                f.airport_dep AS origin_airport,
                f.airport_arr AS destination_airport,
                f.flight_code,
                s.flight_date AS schedule
            FROM 
                flight_ f
            JOIN
                flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
            JOIN 
                schedule_ s ON fs.schedule__flight_date = s.flight_date;"""

        cur.execute(statement, )
        rows = cur.fetchall()

        if len(rows) == 0:
            return jsonify({'status': 400, 'errors': 'No routes found for the given criteria.'}), 400

    # Caso onde temos 2 parametros de entrada
    elif len(routes_payload) == 2 and ("origin_airport" in routes_payload and "destination_airport" in routes_payload):
        statement = """
            SELECT 
                f.airport_dep AS origin_airport,
                f.airport_arr AS destination_airport,
                f.flight_code,
                s.flight_date AS schedule
            FROM 
                flight_ f
            JOIN 
                flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
            JOIN 
                schedule_ s ON fs.schedule__flight_date = s.flight_date
            WHERE 
                f.airport_dep = %s
                AND
                f.airport_arr = %s
            ORDER BY
                f.flight_code;"""

        values = (routes_payload["origin_airport"], routes_payload["destination_airport"],)

        cur.execute(statement, values)
        rows = cur.fetchall()

        if len(rows) == 0:
            return jsonify({'status': 400, 'errors': 'No routes found for the given criteria.'}), 400

    # Caso onde temos 1 parametro de
    elif len(routes_payload) == 1:
        # Caso de termos "origin_airport"
        if 'origin_airport' in routes_payload:
            statement = """
                SELECT 
                    f.airport_dep AS origin_airport,
                    f.airport_arr AS destination_airport,
                    f.flight_code,
                    s.flight_date AS schedule
                FROM 
                    flight_ f
                JOIN 
                    flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
                JOIN 
                    schedule_ s ON fs.schedule__flight_date = s.flight_date
                WHERE 
                    f.airport_dep = %s
                ORDER BY
                    f.flight_code;"""

            values = (routes_payload["origin_airport"],)
        elif "origin_airport" in routes_payload:
            statement = """
                SELECT 
                    f.airport_dep AS origin_airport,
                    f.airport_arr AS destination_airport,
                    f.flight_code,
                    s.flight_date AS schedule
                FROM 
                    flight_ f
                JOIN 
                    flight__schedule_ fs ON f.flight_code = fs.flight__flight_code
                JOIN 
                    schedule_ s ON fs.schedule__flight_date = s.flight_date
                WHERE 
                    f.airport_arr = %s
                ORDER BY
                    f.flight_code;"""

            values = (routes_payload["destination_airport"],)

        cur.execute(statement, values)
        rows = cur.fetchall()

        if len(rows) == 0:
            return jsonify({'status': 400, 'errors': 'No routes found for the given criteria.'}), 400

    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    results_aux = {}
    for row in results_aux:
        key = (row["origin_airport"], row["destination_airport"], row["flight_code"])
        if key not in results_aux:
            results_aux[key] = {"schedules": []}
        results_aux[key]["schedules"].append(row["schedule"])

    results = []
    for key, value in results_aux.items():
        results.append({
            "origin_airport": key[0],
            "destination_airport": key[1],
            "flight_code": key[2],
            "schedules": value["schedules"],
        })
    conn.close()
    return jsonify({'status': 200, 'results': results})


# QUERY 7 -verificada
@app.route('/cloud-query/seats', methods=['GET'])
def check_seats():
    logger.info("###              DEMO: GET /check_seats           ###")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    # Verificação do input

    if len(payload) == 2:
        if "flight_code" and "flight_date" not in payload:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    # Verificar se o voo existe

    statement = """
            SELECT 
                COUNT(*)
            FROM 
                flight_ f
            JOIN 
                schedule_ s ON fs.schedule__flight_date = s.flight_date
            WHERE 
                f.flight_code = %s
                AND
                f.flight_date = %s;"""

    values = (payload["flight_code"], payload["flight_date"],)

    cur.execute(statement, values)
    rows = cur.fetchone()

    if len(rows) != 1:
        return jsonify({'status': 500, 'errors': 'The flight does not exist!'}), 500

    sta = """
SELECT 
    seat_number
FROM 
    seat
WHERE 
    flight__flight_code = %s
    AND schedule__flight_date = %s
    AND available = TRUE;

"""
    val = (payload['flight_code'], payload['schedule_date'])
    cur.execute(sta, val)

    rows = cur.fetchall()
    seat_numbers = [row[0] for row in rows]

    return jsonify({'status': 200, 'result': seat_numbers})


# QUERY 8 - verificada
@app.route('/cloud-query/book_flight', methods=['POST'])
def add_book_flight():
    logger.info("###              DEMO: POST /book_flight             ###");

    conn = db_connection()
    cur = conn.cursor()

    # Só os passageiros podem fazer fazer reservas/pagamentos
    payload = verify_passenger()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    booking_payload = request.get_json()
    logger.info("---- make your booking  ----")
    logger.debug(f'payload: {payload}')

    # Verificação do input

    if len(booking_payload) != 4:
        if "flight_code" and "flight_date" and "ticket_quantity" and "seat_id" not in booking_payload:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    if booking_payload["ticket_quantity"] != len(booking_payload["seat_id"]):
        aux = f"Something is wrong with your request. the number of ticket_quantity, {booking_payload['ticket_quantity']} don't match the number of seats {len(booking_payload['seat_id'])}."
        return jsonify({'status': 400, 'errors': aux}), 400

    # Verificação da disponibilidade de assentos
    statement1 = """
        SELECT COUNT(*) AS available_seats
        FROM seat
        WHERE
        flight__flight_code = %s
        AND schedule__flight_date = %s
        AND seat_number = ANY(%s)
        AND available = TRUE;"""

    values1 = (booking_payload['flight_code'],
               booking_payload['date'],
               booking_payload['seat_id'])

    cur.execute(statement1, values1)
    rows = cur.fetchone()

    if rows[0] != booking_payload['ticket_quantity']:
        aux = f"Something is wrong with your request. Not enough available seats for booking."
        return jsonify({'status': 400, 'errors': aux}), 400

    # Atualizar a disponibilidade dos assentos do booking
    statement2 = """
            UPDATE seat
            SET available = FALSE
            WHERE
                flight__flight_code = %s
                AND schedule__flight_date = %s
                AND seat_number = ANY(%s)
                AND available = TRUE;"""
    values2 = (booking_payload["flight_code"],
               booking_payload["date"],
               booking_payload["seat_id"])

    try:
        cur.execute(statement2, values2)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem (update into seat)!'}), 500

    # Inserção dos dados do booking na tabela
    statement3 = """
            INSERT INTO booking (
                ticket_quantity, 
                ticket_amout_to_pay,
                ticket_amout_payed,
                flight__flight_code, 
                schedule__flight_date,
                passanger_user__id_user
            ) VALUES (
                %s, 
                %s * (SELECT ticket_price FROM flight__schedule_ WHERE flight__flight_code = %s AND schedule__flight_date = %s) ,
                0,
                %s, 
                %s,
                %s
            );"""
    values3 = (booking_payload["ticket_quantity"],
               booking_payload["ticket_quantity"],
               booking_payload["flight_code"],
               booking_payload["date"],
               booking_payload["flight_code"],
               booking_payload["date"],
               payload['id'])

    try:
        cur.execute(statement3, values3)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem (insertion into booking)!'}), 500

    # Verificar e devolver o booking_id gerado.
    statement5 = """
                SELECT booking_id 
                FROM booking 
                WHERE flight__flight_code = %s 
                AND schedule__flight_date = %s
                AND ticket_quantity = %s
                AND passanger_user__id_user= %s
                ORDER BY booking_id DESC
                LIMIT 1
"""
    values5 = (
    booking_payload['flight_code'], booking_payload["date"], booking_payload["ticket_quantity"], payload['id'])

    cur.execute(statement5, values5)
    rows = cur.fetchall()

    if len(rows) != 1:
        aux = f"Something is wrong with your request."
        return jsonify({'status': 500, 'errors': aux}), 500

    conn.close()
    return jsonify(
        {'status': 200, 'results': f"You created successfully your booking. Proceed to payment for booking {rows[0]}."})


# QUERY EXTRA - verificada
@app.route('/cloud-query/tickets', methods=['POST'])
def add_tickets():
    logger.info("###              DEMO: POST /tickets             ###");

    conn = db_connection()
    cur = conn.cursor()

    # Só os passageiros podem fazer pedir tickets!
    payload = verify_passenger()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    tickets_payload = request.get_json()
    logger.info("---- make your tickets  ----")
    logger.debug(f'payload: {payload}')

    # Verificação do input

    if len(tickets_payload) != 2:
        if "booking_id" and "tickets" not in tickets_payload:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    # Verificação se os bilhetes foram criados
    statement0 = """
            SELECT 1
            FROM tickets_
            WHERE booking_booking_id = %s;
            """
    values0 = (tickets_payload['booking_id'],)

    cur.execute(statement0, values0)
    rows = cur.fetchall()

    if rows[0] == 1:
        aux = f"Something is wrong with your request. You already created the tickets."
        return jsonify({'status': 400, 'errors': aux}), 400

    # Verificação dos dados do request
    statement1 = """
            SELECT 1
            FROM booking
            WHERE booking_id = %s
            AND ticket_amout_to_pay = ticket_amout_payed;"""

    values1 = (tickets_payload['booking_id'],)

    cur.execute(statement1, values1)
    rows = cur.fetchall()

    # verificar se a verificação anterior é válida:
    if rows[0] != 1:
        aux = f"Something is wrong with your request. You didn't complete the booking {tickets_payload['booking_id']} payment"
        return jsonify({'status': 400, 'errors': aux}), 400

    # Criação dos bilhetes
    # NOTA: A SUBQUERY PARA IR BUSCAR O FLIGHT_CODE E FLIGHT_DATE PODE SER TRAZIDO DA TABELA BOOKING PQ É O MESMO VOO E HORARIO!
    statement2 = """
            INSERT INTO ticket_(
                name,
                vat,
                booking_booking_id,
                seat_schedule__flight_date,
                seat_flight__flight_code
            ) VALUES(
                %s,
                %s,
                %s,
                (
                    SELECT seat_schedule__flight_date
                    FROM booking 
                    WHERE booking_id = %s;
                ),
                (
                    SELECT seat_flight__flight_code
                    FROM booking
                    WHERE booking_id = %s;
                )
            );"""
    values2 = (tickets_payload["name"],
               tickets_payload["vat"],
               tickets_payload["booking_id"],
               tickets_payload["booking_id"],
               tickets_payload["booking_id"],)

    try:
        cur.execute(statement2, values2)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem (insertion into payment)!'}), 500

    conn.close()
    return jsonify({'status': 200, 'results': "You created successfully your tickets."})


# QUERY 9 - verificada
@app.route('/cloud-query/top_destinations/<n>', methods=['GET'])
def top_destinations(n):
    logger.info("###              DEMO: GET /top_destinations             ###");
    conn = db_connection()
    cur = conn.cursor()

    logger.info("----  Report with the top N destinations ----")
    logger.debug(f'N top destinatons: {n}')

    # Verification of valid input
    try:
        n = int(n)
        if n <= 0:
            return jsonify({'status': 400, 'errors': 'The value for "top_n_flights" should be greater than 1.'}), 400
    except ValueError:
        return jsonify(
            {'status': 400, 'errors': 'The value for "top_n_flights" should be an integer value greater than 1.'}), 400
    except Exception as e:
        return jsonify({'status': 400, 'errors': 'The value for "top_n_flights" is not valid!'}), 400

    current_date = datetime.today()

    statement = """
        SELECT
            f.airport_arr AS destination_airport,
            COUNT(f.flight_code) AS number_flights
        FROM
            flight_ f
        JOIN
            airport_ a ON f.airport_arr = a.airport_code
        WHERE
            DATE(f.arrival_time) >= %s - INTERVAL '12 months'
        GROUP BY
            f.airport_arr
        ORDER BY
        number_flights DESC; """

    values = (current_date,)

    cur.execute(statement, values)
    rows = cur.fetchall()
    # top N destinations. If n>len(rows), rows don't suffer any changes

    if len(rows) == 0:
        return jsonify({'status': 500, 'errors': 'Something went wrong in the system!'}), 500

    rows = rows[:n]

    results = []

    logger.info("---- Check financial data for the last year  ----")
    for row in rows:
        logger.debug(row)
        content = {"destination_airport": row[0], "number_flights": row[1]}
        results.append(content)
    conn.close()
    return jsonify({'status': 200, 'results': results})


# QUERY 10 - verificada
@app.route('/cloud-query/top_routes', methods=['GET'])
def top_routes():
    logger.info("###              DEMO: GET /top_routes             ###");

    conn = db_connection()
    cur = conn.cursor()

    payload = request.get_json()
    logger.info("----  Monthly report with the top N routes with more passengers  ----")
    logger.debug(f'payload: {payload}')

    # Verificação do input

    if len(payload) != 1:
        if "top_n" not in payload:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    n = payload["top_n"]

    # Verification of valid input
    try:
        n = int(n)
        if n <= 0:
            return jsonify({'status': 400, 'errors': 'The value for "top_n_flights" should be greater than 1.'}), 400
    except ValueError:
        return jsonify(
            {'status': 400, 'errors': 'The value for "top_n_flights" should be an integer value greater than 1.'}), 400
    except Exception as e:
        return jsonify({'status': 400, 'errors': 'The value for "top_n_flights" is not valid!'}), 400

    current_date = datetime.today().date()

    statement = """
        SELECT
            TO_CHAR(b.schedule__flight_date, 'YYYY-MM') AS month_year,     
            f.flight_code AS flight_id,                           
            SUM(b.ticket_quantity) AS total_passengers            
        FROM
            booking AS b
        JOIN 
            flight_ AS f ON b.flight__flight_code = f.flight_code
        WHERE 
            b.schedule__flight_date >= %s - INTERVAL '12 months'
            AND b.ticket_amout_payed = 0
        GROUP BY 
            TO_CHAR(b.schedule__flight_date, 'YYYY-MM'),
            f.flight_code
        ORDER BY 
            month_year DESC,
            total_passengers DESC; """

    values = (current_date)

    cur.execute(statement, values)
    rows = cur.fetchall()

    if len(rows) == 0:
        return jsonify({'status': 500, 'errors': 'Something went wrong in the system!'}), 500

    results_aux = {}

    # Get data for each month (month is repeated here)
    for row in rows:
        month = row[0]
        flight_id = row[1]
        total_passengers = row[2]

        if month not in results_aux:
            results_aux[month] = []

        results_aux[month].append({"flight_id": flight_id, "total_passengers": total_passengers})

    # Results to response the top N flights per month
    results = []
    for month, flights in results_aux.items():
        top_n_flights = flights[:n]
        results.append({"month": month, "topN": top_n_flights})

    return jsonify({'status': 200, 'results': results})


# QUERY PARA SABER A QUANTIA NECESSARIA A PAGAR- INFORMAÇÃO SOBRE O BOOKING POR PASSAGEIRO
# verificada
@app.route('/cloud-query/info_booking', methods=['GET'])
def info_booking():
    logger.info("###              DEMO: GET /info_booking             ###");

    conn = db_connection()
    cur = conn.cursor()

    # Só os passageiros podem fazer pagamentos/reservas!
    payload = verify_passenger()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    sta = '''
    SELECT booking_id,ticket_quantity,ticket_amout_to_pay,flight__flight_code,schedule__flight_date FROM booking
WHERE passanger_user__id_user=%s
    '''
    val = payload['id']

    cur.execute(sta, (val,))
    rows = cur.fetchall()
    results = []
    for row in rows:
        row = list(row)
        content = {'booking_id': row[0], 'ticket_quantity': row[1], 'ticket_amout_to_pay': row[2],
                   'flight__flight_code': row[3], 'schedule__flight_date': row[4]}
        results.append(content)
    conn.close()
    return jsonify({'status': 200, 'results': results})


# QUERY 11 - verificada
@app.route('/cloud-query/make_payment', methods=['POST'])
def add_payment():
    logger.info("###              DEMO: POST /make_payment             ###");

    conn = db_connection()
    cur = conn.cursor()

    # Só os passageiros podem fazer pagamentos/reservas!
    payload = verify_passenger()
    if isinstance(payload, tuple):  # Verifica se é um erro (tuple com JSON e status)
        return payload

    payment_payload = request.get_json()
    logger.info("---- make new payment  ----")
    logger.debug(f'payload: {payload}')

    # Verificação do input

    if len(payment_payload) != 5:
        if "flight_code" and "flight_date" and "booking_id" and "method" and "payment_amount" not in payment_payload:
            return jsonify({'status': 400, 'errors': 'Invalid Input. Check the variable names in the request'}), 400
    else:
        return jsonify({'status': 400, 'errors': 'Invalid Input.'}), 400

    # Verificação dos dados do request
    statement1 = """
            SELECT COUNT(*)
            FROM booking AS b
            WHERE b.booking_id = %s
            AND b.ticket_amout_payed >= %s"""

    values1 = (payment_payload['booking_id'], payment_payload['payment_amount'])

    cur.execute(statement1, values1)
    rows = cur.fetchone()

    # verificar se a verificação anterior é válida e se metodo de pagamentp existe:
    if rows[0] != 1 and (payment_payload['method'] in ("Credit Card", "MBWay", "Multibanco reference")):
        aux = f"Something is wrong with your request. Check the values booking_id, method and if the amount you want to pay is valid (less or equal)"
        return jsonify({'status': 500, 'errors': aux}), 500

    # Inserção do pagamento na tabela payment
    statement2 = """
            INSERT INTO payment (amount_payed, payment_date, booking_booking_id)
            VALUES (%s,%s,%s)"""

    # Data com o formato yyyy-mm-dd
    current_date = datetime.today().strftime('%Y-%m-%d')
    values2 = (payment_payload['payment_amount'], current_date, payment_payload['booking_id'])

    try:
        cur.execute(statement2, values2)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem (insertion into payment)!'}), 500

    # Inserção do método de pagamento na tabela payment_method

    statement_aux = """
            SELECT payment_id
            FROM payment
            WHERE booking_booking_id = %s
            ORDER BY payment_date DESC
            LIMIT 1
                    """
    values_aux = (payment_payload['booking_id'],)

    cur.execute(statement_aux, values_aux)
    rows = cur.fetchall()
    if len(rows) == 0:
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem!'}), 500
    payment_id = rows[0]

    statement3 = """
            INSERT INTO payment_method (method, payment_payment_id)
            VALUES (%s,%s)
                """
    values3 = (payment_payload["method"], payment_id)
    try:
        cur.execute(statement3, values3)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify(
            {'status': 500, 'errors': 'Something went wrong in the sistem (insertion into payment_method)!'}), 500

    # Atualização a tabela do booking com o valor que ficou pago

    statement4 = """
            UPDATE booking
            SET ticket_amout_payed = ticket_amout_payed + %s
            WHERE booking_id = %s"""
    values4 = (payment_payload["payment_amount"], payment_payload["booking_id"])
    try:
        cur.execute(statement4, values4)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem!'}), 500

    # Recolha dos dados para a resposta final ao user

    statement5 = """
            SELECT 
                ticket_amout_payed,
                ticket_amout_to_pay - ticket_amout_payed AS remaining_amount
            FROM booking
            WHERE booking_id = %s"""

    values5 = payment_payload["booking_id"]

    cur.execute(statement5, values5)
    rows = cur.fetchall()
    if len(rows) == 0:
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem!'}), 500

    results = f"You paid {rows[0]}€ for your booking {payment_payload['booking_id']}. "
    if rows[1] == 0:
        results += "The payment is completed."
    else:
        results += f"It remains {rows[1]}€ to complete booking payment."

    conn.close()
    return jsonify({'status': 200, 'results': results})



# QUERY 12 - VERIFICADA
@app.route('/cloud-query/financial_data', methods=['GET'])
def financial_data():
    logger.info("###              DEMO: GET /financial_data             ###");

    conn = db_connection()
    cur = conn.cursor()

    statement = """
    SELECT
    b.flight__flight_code,
    SUM(CASE WHEN m.payment_payment_id IS NOT NULL THEN p.amount_payed ELSE 0 END) AS soma_mbway,
    SUM(CASE WHEN cc.payment_payment_id IS NOT NULL THEN p.amount_payed ELSE 0 END) AS soma_credit_card,
    SUM(CASE WHEN dc.payment_payment_id IS NOT NULL THEN p.amount_payed ELSE 0 END) AS soma_debit_card,
    SUM(p.amount_payed) AS total_pago
FROM
    payment p
JOIN
    booking b
    ON p.booking_booking_id = b.booking_id
LEFT JOIN
    mbway m
    ON m.payment_payment_id = p.payment_id
LEFT JOIN
    credit_card cc
    ON cc.payment_payment_id = p.payment_id
LEFT JOIN
    debt_card dc
    ON dc.payment_payment_id = p.payment_id
WHERE
    p.payment_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY
    b.flight__flight_code
ORDER BY
    b.flight__flight_code;
"""

    cur.execute(statement)
    rows = cur.fetchall()
    if len(rows) == 0:
        return jsonify({'status': 500, 'errors': 'Something went wrong in the sistem!'}), 500

    results = []

    logger.info("---- Check financial data for the last year  ----")
    for row in rows:
        logger.debug(row)
        content = {"flight_code": int(row[0]),
                   "Credit Card": float(row[1]),
                   "Debit Card": float(row[2]),
                   "MBWay": float(row[3]),
                   "total": float(row[4])}
        results.append(content)  # appending month report
    conn.close()
    return jsonify({'status': 200, 'results': results})

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
# NOTE: change the host to "db" if you are running as a Docker container
    db = psycopg2.connect(user = "SGD_project",
                        password = "5432",
                        host = "localhost",
                        port = "5433",
                        database = "cloud_query")
    return db


##########################################################
## MAIN
##########################################################
if __name__ == "__main__":
# Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

# create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                          '%H:%M:%S')
                          # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    time.sleep(1) # just to let the DB start before this print :-)


    logger.info("\n---------------------------------------------------------------\n" +
              "API v1.0 online: http://localhost:8080/cloud-query/\n\n")



# NOTE: change to 5000 or remove the port parameter if you are running as a Docker container
    app.run(host="0.0.0.0", port=8080, debug=True, threaded=True)



