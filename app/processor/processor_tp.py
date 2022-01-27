# Transaction Processor - Smart Contract
import traceback
import json
import sys
import hashlib
import logging
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

LOGGER = logging.getLogger(__name__)
DEFAULT_URL = 'tcp://validator:4004'
FAMILY_NAME_CUSTOMER = 'customer'
FAMILY_NAME_BANK = 'bank'

def _hash(data):
    return hashlib.sha512(data).hexdigest()

class BankTransactionHandler(TransactionHandler):  
    def __init__(self, namespace_prefix):
        '''initialization'''
        self._namespace_prefix = namespace_prefix  

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return FAMILY_NAME_BANK
    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return ['1.0']

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.
           The apply function does most of the work for this class by
           processing a transaction for the transaction family.
        '''
        header = transaction.header
        addrs = header.inputs[0] 
        payload_dict = json.loads(transaction.payload.decode())
        action = payload_dict['action']    
        LOGGER.info("ggggggg"+action)
        # user_type = payload_dict['user_type']
        if action=="add bank":
              self._add_bank_(context, addrs,payload_dict)              
        elif action =='update pending list' or action == 'add pending list':
            self._bank_pending_kyc_(context,addrs,payload_dict)
        else:
            LOGGER.info("Unhandled action. Action should be add ")
        

    @classmethod
    def _add_bank_(cls, context, addrs,org_info,timeout=5):
        state_entries=context.get_state([addrs])  
        if state_entries == []:
             LOGGER.info('Adding Bank %s',addrs)
             state_data =  json.dumps(org_info).encode('utf-8')
             addresses = context.set_state({addrs:state_data})
             print(addrs , state_data) 
                         
        else:
            raise InvalidTransaction("User already exists")
    def _bank_pending_kyc_(cls, context, addrs,org_info,timeout=5):
        LOGGER.info('inside bank pending kyc')
        state_entries=context.get_state([addrs])  
        if state_entries == []:
             LOGGER.info('Initalizing and adding to   Pending list %s',addrs)
        else:
             LOGGER.info(' Adding to  Pending list %s',addrs)
        state_data =  json.dumps(org_info).encode('utf-8')
        addresses = context.set_state({addrs:state_data})
        print(addrs , state_data)
    

# CUSTOMER TRANSACTION HANDLER
class CustomerTransactionHandler(TransactionHandler):  
    def __init__(self, namespace_prefix):
        '''initialization'''
        self._namespace_prefix = namespace_prefix  

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return FAMILY_NAME_CUSTOMER
    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return ['1.0']

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.
           The apply function does most of the work for this class by
           processing a transaction for the transaction family.
        '''
        header = transaction.header
        addrs = header.inputs[0] 
        payload_dict = json.loads(transaction.payload.decode())
        action = payload_dict['action']    
        # user_type = payload_dict['user_type']
        if action=="add customer":
              self._add_customer_(context, addrs,payload_dict)  
        elif action == 'add new kyc':
              self._add_new_kyc_(context,addrs,payload_dict)   
        elif action == 'update kyc details':
              self._update_kyc_(context,addrs,payload_dict)  
        elif action == 'update customer':
              self._update_customer_(context, addrs,payload_dict) 
        elif action == 'add pending bank' or action == 'update pending bank':
              self._customer_pending_banks_(context, addrs,payload_dict)
        else:
            LOGGER.info("Unhandled action. Action should be add ")
        

    @classmethod
    def _add_customer_(cls,context, addrs,org_info,timeout=5):
        state_entries=context.get_state([addrs])  
        if state_entries == []:
             LOGGER.info('Registering user %s',addrs)
             state_data =  json.dumps(org_info).encode('utf-8')
             addresses = context.set_state({addrs:state_data})
             print(addrs , state_data)             
        else:
            raise InvalidTransaction("User already exists") 
    @classmethod
    def _update_customer_(cls,context, addrs,org_info,timeout=5):
        state_entries=context.get_state([addrs])  
        if state_entries == []:
            raise InvalidTransaction("User does not exists") 
        else:
            LOGGER.info('Updating user %s',addrs)
            state_data =  json.dumps(org_info).encode('utf-8')
            addresses = context.set_state({addrs:state_data})
            print(addrs , state_data)    
    
    @classmethod
    def _add_new_kyc_(cls, context, addrs,org_info,timeout=5):
        state_entries=context.get_state([addrs])  
        if state_entries == []:
             LOGGER.info('Registering new KYC %s',addrs)
             state_data =  json.dumps(org_info).encode('utf-8')
             addresses = context.set_state({addrs:state_data})
             print(addrs , state_data)             
        else:
            raise InvalidTransaction("KYC number already exists")    
    
    @classmethod
    def _update_kyc_(cls,context, addrs,org_info,timeout=5):
        state_entries=context.get_state([addrs])  
        if state_entries == []:
            raise InvalidTransaction("KYC number does not exist") 
        else:
            LOGGER.info('Updating KYC details %s',addrs)
            state_data =  json.dumps(org_info).encode('utf-8')
            addresses = context.set_state({addrs:state_data})
            print(addrs , state_data)  
    
    @classmethod
    def _customer_pending_banks_(cls, context, addrs,org_info,timeout=5):
        LOGGER.info('insidecustomer requests')
        state_entries=context.get_state([addrs])  
        if state_entries == []:
             LOGGER.info('Initalizing and adding to   Pending banks %s',addrs)
        else:
             LOGGER.info(' Adding to  Pending banks %s',addrs)
        state_data =  json.dumps(org_info).encode('utf-8')
        addresses = context.set_state({addrs:state_data})
        print(addrs , state_data)


def main():
    '''Entry-point function for the Transaction Processor.'''
    try:
        # Setup logging for this class.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        # Register the Transaction Handler and start it.
        processor = TransactionProcessor(url=DEFAULT_URL)
        bank_namespace = _hash(FAMILY_NAME_BANK.encode('utf-8'))[0:6]
        handler_1 = BankTransactionHandler(bank_namespace)
        
        customer_namespace = _hash(FAMILY_NAME_CUSTOMER.encode('utf-8'))[0:6]
        handler_2 = CustomerTransactionHandler(customer_namespace)

        processor.add_handler(handler_1)
        processor.add_handler(handler_2)
        processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

