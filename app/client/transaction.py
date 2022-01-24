#transaction
import hashlib
import base64
import json
import random
import time
import requests
import yaml
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
FAMILY_NAME_BANK = 'bank'




def _hash(data):
    return hashlib.sha512(data).hexdigest()

def create_address(mode='user',name='name',private_key='key',family_name='default'):
     return _hash(family_name.encode())[:6]+_hash(mode.encode())[:6]+_hash(name.encode())[:52]+_hash(str(private_key).encode())[:6]


class KycbankClient(object):
    '''Client  class
    
    Supports "create" function.
    '''

    def __init__(self, base_url, key=None,signer=None,public_key=None):
        '''Initialize the client class.
        '''
        self._base_url = base_url
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
        

    
     
     
    def add(self,org_info,password):
        '''
        Adds a new party to blockchain
        '''
        print('inside add tx.py')
        print('address')
        paddr=create_address(mode=password,name=org_info['name'],private_key=self._private_key,family_name = FAMILY_NAME_ORG)
        print(paddr)
        print(org_info)
        org_info['action'] ='add'
        result = self._wrap_and_send(paddr,org_info,family_name = FAMILY_NAME_ORG)
    



  


    
    
		
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
