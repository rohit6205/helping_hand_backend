from flask import Flask, jsonify, request, flash, redirect, url_for
from mysql.connector import connect, Error
from flask_cors import CORS, cross_origin

STRING_FAIL = 'fail'
STRING_SUCCESS = 'success'

def get_db_connection():
    try:
        connection = connect(host="localhost", user="<username>", password="<password>", database="<DB>")
        app.logger.info('Database connected Successfully %s', connection)
    except Error as e:
        app.logger.error('Error Occured while connecting to Database - %s', e)
        return None
    return connection

def get_serialize_data(fields, results):

    column_list = []

    for i in fields:
        column_list.append(i[0])

    jsonData_list = []
    for row in results:
        data_dict = {}
        for i in range(len(column_list)):
            data_dict[column_list[i]] = row[i]
        if data_dict.get('phoneNumber', None):
            data_dict['phoneNumber'] = data_dict['phoneNumber'].split('/')
        jsonData_list.append(data_dict)
    return jsonData_list

def get_structured_cities(cities):
    new_structure = []
    for value in cities:
        data = {"label": value["city"], "value": value["city"]}
        new_structure.append(data)
    return new_structure

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#app.config['SECRET_KEY'] = 'hardsecretkey'

@app.route("/")
@cross_origin()
def hello():
    return "Hello, Flask!"

@app.route("/api/cities")
@cross_origin()
def get_cities():
    medicine = request.args.get('medicine')
    state = request.args.get('state')

    app.logger.info('Fetching city for medicine - %s and state - %s', medicine, state)
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        get_query = """select distinct(city) from distributors left join medicine on distributors.distributorID = medicine.distributorID where state=%s and medicineName=%s""" % (state, medicine)
        cursor.execute(get_query)
        city = cursor.fetchall()
        fields_list = cursor.description
    else:
        app.logger.error('Counld not get data from table as connection is - %s', conn)
        return jsonify(meta=STRING_FAIL)
    cursor.close()
    conn.close()
    json_data_list = get_structured_cities(get_serialize_data(fields_list, city))
    response = jsonify(meta=STRING_SUCCESS, response=json_data_list)
    return response

@app.route('/api/distributors', methods=['GET'])
@cross_origin()
def get_all_medicine():

    medicine = request.args.get('medicine')
    city = request.args.get('city')

    app.logger.info('Fetching data for medicine - %s and city - %s', medicine, city)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        get_query = """select * from distributors left join medicine on distributors.distributorID = medicine.distributorID where city=%s and medicineName=%s""" % (city, medicine)
        app.logger.info('select query - %s', get_query)
        cursor.execute(get_query)
        medicine_details = cursor.fetchall()
        fields_list = cursor.description
    else:
        app.logger.error('Counld not get data from table as connection is - %s', conn)
        return jsonify(meta=STRING_FAIL)

    cursor.close()
    conn.close()

    json_data_list = get_serialize_data(fields_list, medicine_details)

    response = jsonify(meta=STRING_SUCCESS, response=json_data_list)
    #response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/api/feedback/submit', methods=['POST'])
@cross_origin()
def save_feedback():
    """
    {
            distributorID: 12,
            feedbackCodes: ['ABC', 'XYZ']
            }
    """
    feedback_data = request.get_json(force=True)
    feedback_codes = feedback_data['feedbackCodes']
    feedback_value = [1] * len(feedback_codes)
    if len(feedback_codes) == 0:
        return jsonify(meta=STRING_SUCCESS, response='No feedback to store in table')
    feedback_codes.append('distributorID')
    feedback_value.append(feedback_data['distributorID'])

    app.logger.info('data to be store in feedback table - %s', feedback_data)
    conn = get_db_connection()
    try:
        if conn:
            cursor = conn.cursor()
            #get_query = """insert into feedback %s values %s""" % (tuple(feedback_codes), tuple(feedback_value))
            get_query = "insert into feedback ("
            get_query += ','.join(feedback_codes)
            get_query += ') values '
            get_query += str(tuple(feedback_value))
            print(get_query)
            cursor.execute(get_query)
        else:
            conn.commit()
            cursor.close()
            conn.close()
            app.logger.error('Counld not get data from table as connection is - %s', conn)
            return jsonify(meta=STRING_FAIL)
    except Error as e:
        app.logger.error('FEEDBACK - Error Occured while storing into table - %s', e)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify(meta=STRING_FAIL)

    conn.commit()
    cursor.close()
    conn.close()

    response = jsonify(meta=STRING_SUCCESS, response='Feedback Stored Successfully')
    return response

if __name__ == '__main__' :
    app.run(debug=True)
