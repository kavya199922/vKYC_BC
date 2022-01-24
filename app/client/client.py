from flask import Flask,jsonify,request
from client import *
app = Flask(__name__)


@app.route('/signup',methods=['GET','POST'])
#{"name":"HDFC","private_key":"","password":"","requests":[{"kyc_no":"","value":"ACCEPTED/REJECTED"}],"user_type":"BANK/BANK EMPLOYEE/CUSTOMER"}
def signup_user():
    info = request.get_json(force=True)
    print(org_info)
    password = info['password']
    del info['password']
    resp = create_user(info,password)
    return jsonify(private_key=resp)


# @app.route('/login',methods=['GET','POST'])
# def login_org():
#     org_info = request.get_json(force=True)
#     resp = get_orginfo(org_info['name'],org_info['private_key'],org_info['password']) 
#     return jsonify(data=json.loads(resp[0].decode('utf-8')))
    




if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=9090)