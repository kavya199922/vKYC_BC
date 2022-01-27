#transaction
import hashlib
import base64
import json
import random
import time
import requests
import yaml
import datetime
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

# The Transaction Family Name
FAMILY_NAME_CUSTOMER = 'customer'
FAMILY_NAME_BANK = 'bank'




def _hash(data):
    return hashlib.sha512(data).hexdigest()

def create_address(mode='user',name='name',private_key='key',family_name='default'):
     return _hash(family_name.encode())[:6]+_hash(mode.encode())[:6]+_hash(name.encode())[:52]+_hash(str(private_key).encode())[:6]


class KycClient(object):
    '''Client  class
    
    Supports "create" function.
    '''

    def __init__(self, key=None,signer=None,public_key=None):
        '''Initialize the client class.
        '''
        self._base_url = 'http://10.168.126.150:8008'
        if key is None:
            self._signer = None
            return
        private_key = Secp256k1PrivateKey.from_hex(key)
        context = create_context('secp256k1')
        signer = CryptoFactory(context).new_signer(private_key)
        public_key = signer.get_public_key().as_hex()
        self._signer = signer
        self._public_key = public_key
        print('Public-Key is ',self._public_key)
        print(len(self._public_key))
        self._private_key = key

    def add_kyc_details(self,kyc_details):
        kyc_details['kyc_data']['status'] = 'SUBMITTED'
        kyc_number = str(_hash(kyc_details['user_data']['mobile_number'].encode('utf-8'))[:6] + _hash('customer'.encode('utf-8'))[:4])
        kyc_data={kyc_number:kyc_details['kyc_data']}
        kyc_data['action'] ='add new kyc'
        paddr = _hash('kyc_customer'.encode('utf-8'))[0:35] + _hash(kyc_number.encode('utf-8'))[0:35] 
        # #create address : kyc -add(C),status_change(BankEmployee only if status : submitted and assigned to is bank of that employee),View(ALL)
        result = self._wrap_and_send(paddr,kyc_data,family_name = FAMILY_NAME_CUSTOMER)
        # result = json.loads(result)
        #update kyc number in customer data 
        user_data = kyc_details['user_data']
        user_data['kyc_number'] = kyc_number
        user_data['action'] = 'update customer'
        paddr=create_address(mode=kyc_details['user_data']['password'],name=user_data['mobile_number'],private_key=self._private_key,family_name = FAMILY_NAME_CUSTOMER)
        result = self._wrap_and_send(paddr,user_data,family_name = FAMILY_NAME_CUSTOMER)
        # add to pending lists in bank
        response = self.update_pending_lists_bank(kyc_details['kyc_data']['assigned_to'],kyc_number)
        print('-----------------')
        print(response)
        return kyc_number
    def update_pending_lists_bank(self,bank_name,kyc_number,action=''):
        paddr = _hash('pending_bank'.encode('utf-8'))[0:35] + _hash(bank_name.encode('utf-8'))[0:35]
        print(paddr)
        res = requests.get(url = self._base_url+"/state/{}".format(paddr))
        print(res.status_code,type(res.status_code))

        if res.status_code== 404:
            print('000')
            # create pending lists
            pending_lists = [kyc_number]
            data = {'bank_name':bank_name,"pending_list":pending_lists,'action':'add pending list'}        
            result = self._wrap_and_send(paddr,data,family_name = FAMILY_NAME_BANK)
        else:
            print('inside else')
            pending_lists= json.loads(base64.b64decode(yaml.safe_load(res.text)["data"]).decode('utf-8'))
            # print(pending_lists)
            if action == 'pop':
                print('going to update')
                print(pending_lists)
                pending_lists['pending_list'].remove(kyc_number)
            else:
                print(pending_lists)
                pending_lists['pending_list'].append(kyc_number)
            print(pending_lists)
            data = {'bank_name':bank_name,"pending_list":pending_lists['pending_list'],'action':'update pending list'}
            result = self._wrap_and_send(paddr,data,family_name = FAMILY_NAME_BANK)
        return result
    
    def update_pending_requests_customer(self,bank_name,kyc_number,action=''):
        paddr = _hash('pending_customer'.encode('utf-8'))[0:35] + _hash(kyc_number.encode('utf-8'))[0:35]
        print(paddr)
        res = requests.get(url = self._base_url+"/state/{}".format(paddr))
        print(res.status_code,type(res.status_code))

        if res.status_code== 404:
            print('000')
            # create pending lists
            pending_lists = [bank_name]
            data = {"kyc_number":kyc_number,"pending_banks":pending_lists,'action':'add pending bank'}        
            result = self._wrap_and_send(paddr,data,family_name = FAMILY_NAME_CUSTOMER)
        else:
            print('inside else')
            pending_lists= json.loads(base64.b64decode(yaml.safe_load(res.text)["data"]).decode('utf-8'))
            print(pending_lists)
            if action == 'pop':
                print('going to update')
                print(pending_lists)
                pending_lists['pending_banks'].remove(bank_name)
            else:
                pending_lists['pending_banks'].append(bank_name)
            print(pending_lists)
            data = {"kyc_number":kyc_number,"pending_banks":pending_lists['pending_banks'],'action':'update pending bank'}
            result = self._wrap_and_send(paddr,data,family_name = FAMILY_NAME_CUSTOMER)
        return result
    
    def view_pending_lists(self,user_data):
         paddr = _hash('pending_bank'.encode('utf-8'))[0:35] + _hash(user_data['user_data']['bank_name'].encode('utf-8'))[0:35]
         res = requests.get(url = self._base_url+"/state/{}".format(paddr))
         print(res.status_code)
         if res.status_code ==404:
             print(paddr)
             return "No Data"
         else:
            response = (base64.b64decode(yaml.safe_load(res.text)["data"]))
            return json.loads(response.decode('utf-8'))
    def view_customer_pending_banks(self,user_data):
        paddr = _hash('pending_customer'.encode('utf-8'))[0:35] + _hash(user_data['kyc_number'].encode('utf-8'))[0:35]
        print(paddr)
        res = requests.get(url = self._base_url+"/state/{}".format(paddr))
        print(res.status_code)
        if res.status_code ==404:
            return "No Data"
        else:
            response = (base64.b64decode(yaml.safe_load(res.text)["data"]))
            return json.loads(response.decode('utf-8'))


    
    def verify_kyc_details(self,data):
        kyc_number = data['kyc_number']
        bank_name = data['user_data']['bank_name']
        status = data['status']
        paddr = _hash('kyc_customer'.encode('utf-8'))[0:35] + _hash(kyc_number.encode('utf-8'))[0:35] 
        res = requests.get(url = self._base_url+"/state/{}".format(paddr))
        response = json.loads((base64.b64decode(yaml.safe_load(res.text)["data"])).decode('utf-8'))
        print(response)
        allowed_banks = [ bank['bank_name'] for bank in  response[kyc_number]['allowed_banks']]
        if bank_name in allowed_banks:
            # update customer kyc status 
             kyc_data = response
             kyc_data[kyc_number]['status'] = status
             kyc_data['action'] = 'update kyc details'
             paddr = _hash('kyc_customer'.encode('utf-8'))[0:35] + _hash(kyc_number.encode('utf-8'))[0:35] 
             result = self._wrap_and_send(paddr,kyc_data,family_name = FAMILY_NAME_CUSTOMER)
             print('000')
             print(result,json.loads(result))
            #  result = json.loads((base64.b64decode(yaml.safe_load(result)["data"])).decode('utf-8'))
            #  remove from pending lists
             self.update_pending_lists_bank(bank_name,kyc_number,action='pop')
        else:
            result = 'not Allowed'
        print(result)
        return result
    
    def request_kyc_details(self,data):
        bank_name_url = data['user_data'] 
        kyc_number= data['kyc_number']
        # push to pending requests in customer Tx Family
        result = self.update_pending_requests_customer(bank_name_url['bank_name'],kyc_number)
        return result



    def accept_kyc_request(self,data):
        # HDFC: ICICIC 
        bank_name_url = data['user_data']
        kyc_number= data['kyc_number']
        paddr = _hash('kyc_customer'.encode('utf-8'))[0:35] + _hash(kyc_number.encode('utf-8'))[0:35] 
        res = requests.get(url = self._base_url+"/state/{}".format(paddr))
        response = json.loads((base64.b64decode(yaml.safe_load(res.text)["data"])).decode('utf-8'))
        # add banks to allowed banks
        response[kyc_number]['allowed_banks'].append(bank_name_url)
        paddr = _hash('kyc_customer'.encode('utf-8'))[0:35] + _hash(kyc_number.encode('utf-8'))[0:35] 
        result = self._wrap_and_send(paddr,response,family_name = FAMILY_NAME_CUSTOMER)
        # remove bank from pending requests
        result = self.update_pending_requests_customer(bank_name_url['bank_name'],kyc_number,action='pop')
        return response
    
    def reject_kyc_request(self,data):
        bank_name_url = data['user_data'] 
        kyc_number= data['kyc_number']
        # remove bank from pending requests
        result = self.update_pending_requests_customer(bank_name['bank_name'],kyc_number,action='pop')
        return response

    
    def view_kyc_details(self,data):
        paddr = _hash('kyc_customer'.encode('utf-8'))[0:35] + _hash(data['kyc_number'].encode('utf-8'))[0:35] 
        res = requests.get(url = self._base_url+"/state/{}".format(paddr))
        print(res)
        response = json.loads((base64.b64decode(yaml.safe_load(res.text)["data"])).decode('utf-8'))
        bank_name = data['user_data']['bank_name'] if 'bank_name' in data['user_data'] else ''
        kyc_number = data['kyc_number']
        # "allowed_banks":[{"bank_name":},{"bank_name":},{"bank_name":}]
        
        if data['user_data']['user_type'] == 'customer' or (data['user_data']['user_type'] == 'bank' and bank_name in  [ bank['bank_name'] for bank in  response[kyc_number]['allowed_banks']]):
            return response
        else:
            return "Not Allowed to view"




    







    def login_user(self,identifier,password,user_type):
        '''
        displays info of the user
        '''
        print(user_type)
        user_type = user_type.upper()
        print(eval('FAMILY_NAME_'+user_type.upper()))
        paddr=create_address(mode=password,name=identifier,private_key=self._private_key,family_name = eval('FAMILY_NAME_'+user_type))
        print(paddr)
        res = requests.get(url = self._base_url+"/state/{}".format(paddr))
        print(res.status_code,type(res.status_code))
        if res.status_code == 404:
             ans ={}
             ans['status'] = 'login failed'
             return ans 
        else:
            ans= base64.b64decode(yaml.safe_load(res.text)["data"])
            ans = json.loads(ans.decode('utf-8'))
            ans['status'] = 'login success'
            return ans
        

    def create_user(self,info,password):
        '''
        Adds a new party to blockchain - customer/bank
        '''
        print('inside add tx.py')
        print('address')
        print(info)
        operation = {'add bank':{'family':FAMILY_NAME_BANK,'name':'identifier'},'add customer':{'family':FAMILY_NAME_CUSTOMER,'name':'mobile_number'}}
        info['action'] ='add bank' if info['user_type'] =='BANK' else 'add employee' if  info['user_type'] =='BANK EMPLOYEE' else 'add customer'
        paddr=create_address(mode=password,name=info[operation[info['action']]['name']],private_key=self._private_key,family_name = operation[info['action']]['family'])
        print(info)
        result = self._wrap_and_send(paddr,info,family_name = operation[info['action']]['family'])
        print(result)
        result = json.loads(result)
        return result['data'][0]['status']
	
    def _send_to_rest_api(self, suffix, data=None, content_type=None):
        '''
        sends request to rest api
        '''
        # print('inside rest api')
        url = "{}/{}".format(self._base_url, suffix)
        # print("URL to send to REST API is {}".format(url))

        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                print('going to hit')
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if not result.ok:
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))
        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))
        except BaseException as err:
            raise Exception(err)

        return result.text,result.status_code

    def _wait_for_status(self, batch_id, wait, result):
        '''
        waits for result from rest api
        '''
        if wait and wait > 0:
            waited = 0
            start_time = time.time()
            while waited < wait:
                result,result_status = self._send_to_rest_api("batch_statuses?id={}&wait={}"
                                               .format(batch_id, wait))
                status = yaml.safe_load(result)['data'][0]['status']
                waited = time.time() - start_time

                if status != 'PENDING':
                    return result
            return "Transaction timed out after waiting {} seconds." \
               .format(wait)
        else:
            return result,result_status


    def _wrap_and_send(self,address,org_info,uaddress='',family_name=''):
        '''
        create and send transactions in batches  
        '''
        
        payload =json.dumps(org_info).encode()
        input_and_output_address_list=[]
        if uaddress=='':
            input_and_output_address_list = [address]
        else:
            input_and_output_address_list=[address,uaddress] 
        print('wrap and send')
        print(input_and_output_address_list)   
        header = TransactionHeader(
            signer_public_key=self._public_key,
            family_name=family_name,
            family_version="1.0",
            inputs=input_and_output_address_list,
            outputs=input_and_output_address_list,
            dependencies=[],
            payload_sha512=_hash(payload),
            batcher_public_key=self._public_key,
            nonce=random.random().hex().encode()
        ).SerializeToString()

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        transaction_list = [transaction]

        header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in transaction_list]
        ).SerializeToString()

        batch = Batch(
            header=header,
            transactions=transaction_list,
            header_signature=self._signer.sign(header))

        batch_list = BatchList(batches=[batch])
        batch_id = batch_list.batches[0].header_signature

        result,result_status = self._send_to_rest_api("batches",
                                       batch_list.SerializeToString(),
                                       'application/octet-stream')
        wait =10
        # print(result_status)
        return self._wait_for_status(batch_id, wait, result)
