import json
from flask import Flask,jsonify,request
from sawtooth_signing import create_context
from transaction import KycClient
app = Flask(__name__)


@app.route('/signup',methods=['GET','POST'])
def signup_user():
    info = request.get_json(force=True)
    password = info['password']
    del info['password']
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    client = KycClient(key=private_key.as_hex())
    # print(help(client))
    result = client.create_user(info,password)
    # print(res)
    return jsonify(private_key=str(private_key.as_hex()),result_status=result)
@app.route('/login',methods=['GET','POST'])
def login():
    info = request.get_json(force=True)
    client = KycClient(key=info['private_key'])
    resp = client.login_user(info['identifier'],info['password'],info['user_type'])
    return jsonify(data=json.loads(resp.decode('utf-8')))
@app.route('/add_kyc',methods= ['GET','POST'])
def add_kyc():
    kyc_details = request.get_json(force=True)
    client = KycClient(key = kyc_details['user_data']['private_key'])
    resp = client.add_kyc_details(kyc_details)
    return jsonify(data=resp)
@app.route('/view_pending_lists',methods=['GET','POST'])
def view_pending():
    details = request.get_json(force=True)
    client = KycClient(key = details['user_data']['private_key'])
    resp = client.view_pending_lists(details)
    return jsonify(data=resp)
@app.route('/verify_kyc',methods= ['GET','POST'])
def verify_kyc():
    details = request.get_json(force=True)
    client = KycClient(key = details['user_data']['private_key'])
    resp = client.verify_kyc_details(details)
    return jsonify(data=resp)

@app.route('/request_kyc_details',methods= ['GET','POST'])
def request_kyc():
    details = request.get_json(force=True)
    client = KycClient(key = details['user_data']['private_key'])
    resp = client.request_kyc_details(details)
    return jsonify(data=resp)

@app.route('/accept_kyc_request',methods= ['GET','POST'])
def accept_kyc():
    details = request.get_json(force=True)
    client = KycClient(key = details['user_data']['private_key'])
    resp = client.accept_kyc_request(details)
    # print(resp)
    return jsonify(data=resp)

@app.route('/reject_kyc_request',methods= ['GET','POST'])
def reject_kyc():
    details = request.get_json(force=True)
    client = KycClient(key = details['user_data']['private_key'])
    resp = client.reject_kyc_request(details)
    return jsonify(data=resp)

@app.route('/view_kyc_details',methods= ['GET','POST'])
def view_kyc():
    details = request.get_json(force=True)
    client = KycClient(key = details['user_data']['private_key'])
    resp = client.view_kyc_details(details)
    return jsonify(data=resp)

@app.route('/view_pending_banks',methods=['GET','POST'])
def view_pending_banks():
    details = request.get_json(force=True)
    client = KycClient(key = details['user_data']['private_key'])
    resp = client.view_customer_pending_banks(details)
    return jsonify(data=resp)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=9090)