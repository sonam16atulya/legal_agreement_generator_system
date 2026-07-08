from flask import Flask, request, jsonify
from aws.s3_utils import aws_file_upload
from doc2sign.docusign import convert_to_base64, envelope_status_check, generate_ids, send_email_doc
from doc2sign.populate_file import calc_expiry_date, extract_valid_period, populate_file
from flask_cors import CORS
from datetime import datetime
import random
from env import credentials
from reminder.notification import check_envelops  # Make sure check_envelops is imported correctly
import os
from flask import send_file, make_response
from dynamo.models import *
from flask import Flask, render_template


app = Flask(__name__)
CORS(app)

base =  credentials.get('fbase_url') 


# # Initialize APScheduler
# scheduler = BackgroundScheduler()

# # Define your scheduled task using APScheduler
# @scheduler.scheduled_job(CronTrigger(hour=9, minute=0))
# def my_daily_task():
#     print("Running daily task at 9:00 am")
#     check_envelops()

# Health check endpoint
@app.route('/legal/health', methods=['GET'])
def health_check():
    health_status = {
        'status': 'ok'
    }
    return jsonify(health_status), 200

# Route to handle file upload
@app.route('/legal/api/upload', methods=['POST'])
def upload_file():
    r_id = random.randint(1, 1000)

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    image_path = request.files.get('image')

    file_url = aws_file_upload(file, 'test', f'{r_id}_uploaded.csv', True)
    filled_document, data, temp_file_path = populate_file(
        file, 'agreement.docx', image_path, r_id)

    # For DynamoDB (assuming these functions are defined in models)
    dynamo_insert_agreement({
        "id": int(r_id),
        "registered_entity_name": str(data.get('[registered_entity_name]')),
        "cin": str(data.get('[CIN]')),
        "name": request.form.get('name'),
        "email": None,
        "subject": None,
        "uploaded_file": file_url,
        "temp_file_path": '',
        "final_link": None,
        "date_of_agreement": str(datetime.today())
    })

    return jsonify({"link": filled_document, 'id': str(r_id), 'temp_file_path': temp_file_path, 'name': request.form.get('name'),'uploaded_file': file_url}), 200


@app.route('/legal/api/send-envelops', methods=['POST'])
def send_envelops():
    is_file = False
    file_path = request.form.get('file_path', None)
    if not file_path:
        is_file = True
        file_path = request.files['file']

    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')

    file_url = aws_file_upload(
        file_path, 'test', f'{str(request.form.get("id"))}_final.docx', is_file)

    valid_period = int(extract_valid_period(file_path))
    expiry_date = calc_expiry_date(valid_period)

    filter_val = int(request.form.get('id'))
    res = send_email_doc(str(convert_to_base64(file_path, is_file)),
                         generate_ids(), email, subject, name, generate_ids(), credentials.get('account_id') )
    data = {
        "final_link": file_url,
        "email": str(request.form.get('email')),
        "subject":  str(request.form.get('subject')),
        "validity": valid_period,
        "expiry_date": expiry_date,
        "envelope_id": res['envelopeId'],
        "r_id": filter_val
    }
    dynamo_update_agreement(filter_val, data)

    if not is_file:
        os.remove(file_path)

    return jsonify({'message': 'Envelops sent successfully', 'response': res}), 200

# Route to get envelops
@app.route('/legal/api/get-envelops', methods=['GET'])
def get_envelops():
    envelops = dynamo_get_agreement()
    for i in envelops:
        try:
            if i['r_id']:
                status = envelope_status_check(credentials.get('account_id'), i['envelope_id'])
                dynamo_update_agreement(int(i['r_id']), {'envelope_status': status['status']})
        except:
            pass
    return jsonify(envelops), 200

# Route to get counts
@app.route('/legal/api/get-counts', methods=['GET'])
def get_counts():
    count_data = {
        'renewal_count': 300,
        'expiring_next_month': 20,
        'total_agreement': 500
    }
    return jsonify(count_data), 200



@app.route('/legal/api/notify', methods=['GET'])
def notify():
    result = check_envelops()
    if result:
        return jsonify({'message': result}), 200
    else:
        return jsonify({'message': 'Failed to send notification'}), 400


# Frontend Added

@app.route('/')
def index():
    return render_template('index.html', base = base)


@app.route('/form/index.html')
def index1():
    return render_template('form/index.html', base = base)


@app.route('/form/final_page.html')
def index2():
    return render_template('form/final_page.html', base = base)


if __name__ == '__main__':
     app.run(debug=False)
