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
        return FAMILY_NAME_ORG
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
        if action=="add":
              self._create_org(context, addrs,payload_dict)              
        else:
            LOGGER.info("Unhandled action. Action should be add ")
        

    @classmethod
    def _create_bank(cls, context, addrs,org_info,timeout=5):
        state_entries=context.get_state([addrs])  
        if state_entries == []:
             LOGGER.info('Registering new bank %s',addrs)
             state_data =  json.dumps(org_info).encode('utf-8')
             addresses = context.set_state({addrs:state_data})
             print(addrs , state_data)
            #  cls.append_all_org_data(context,org_info)
             
        else:
            raise InvalidTransaction("Bank already exists")    


def main():
    '''Entry-point function for the Transaction Processor.'''
    try:
        # Setup logging for this class.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

        # Register the Transaction Handler and start it.
        processor = TransactionProcessor(url=DEFAULT_URL)
        bank_namespace = _hash(FAMILY_NAME_BANK.encode('utf-8'))[0:6]
        handler = BankTransactionHandler(sw_namespace)
        processor.add_handler(handler)
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

