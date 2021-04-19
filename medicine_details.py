from flask import Flask, jsonify, request, flash, redirect, url_for
from mysql.connector import connect, Error

STRING_FAIL = 'fail'
STRING_SUCCESS = 'success'

def get_db_connection():
    try:
        connection = connect(host="localhost", user='', password='')
        app.logger.info('Database connected Successfully %s', connection)
    except Error as e:
        app.logger.error('Error Occured while connecting to Database - %s', e)
        return None
    return connection

def get_serialize_data(fields, results):
    
    column_list = []
    
    for i in fields_list:
        column_list.append(i[0])

    jsonData_list = []
    for row in result_list:
        data_dict = {}
        for i in range(len(column_list)):
            data_dict[column_list[i]] = row[i]
        jsonData_list.append(data_dict)
    return jsonData_list


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hardsecretkey'


@app.route('/api/distributors', methods=['GET'])
def get_all_medicine():
    
    medicine = request.args.get('medicine')
    city = request.args.get('city')
    
    app.logger.info('Fetching data for medicine - %s and city - %s', medicine, city)

    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        medicine_details = cursor.execute("""select * from distributor left join medicine /
                    on distributor.distributorID = medicine.distributorID;""").fetchall()
        fields_list = cursor.description
    else:
        app.logger.error('Counld not get data from table as connection is - %s', conn)
        return jsonify(meta=STRING_FAIL)
    
    cursor.close()
    conn.close()

    json_data_list = get_serialize_data(fields_list, medicine_details)

    return jsonify(meta=STRING_SUCCESS, user=json_data_list.toString())


if __name__ == '__main__' :
    app.run(debug=True)
