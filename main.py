from lndgrpc import LNDClient
import lndgrpc.rpc_pb2 as ln
import configparser
from time import sleep
import json
import yaml

def create_node_obj(config, name):
    invoice_mac_loc = config[name]["admin_mac_loc"]
    tls_cert_loc = config[name]["tls_cert_loc"]
    ip_address = config[name]["address"]

    # pass in the ip-address with RPC port and network ('mainnet', 'testnet', 'simnet')
    # the client defaults to 127.0.0.1:10009 and mainnet if no args provided
    node_obj = LNDClient(macaroon_filepath=invoice_mac_loc, cert_filepath=tls_cert_loc, network="simnet",
                         ip_address=ip_address)

    return node_obj

def get_share_policy(memo):
    with open('shares.config') as f:
        conf = yaml.safe_load(f)
        for key in conf.keys():
            if key in memo:
                return conf[key]
        return False


def check_invoice_paid():
    pass


def main():
    config = configparser.ConfigParser()
    config.read("project.config")

    alice = create_node_obj(config, "alice")
    bob = create_node_obj(config, "bob")
    # carol_pub = "02aa93525d98c65c1b1bbe6486fc3b5918657ba8664065906c356c14288da78621"
    # dave_pub = "0283b2f17ef004426f545a9b84c86e7edca548ef5029218fdce9b8bd2979aea83b"
    # erin_pub = "0227f7850fcd6d33b8dbe589232619e6b17fc8b22cbcf9a136bf17f93c0bbd3c24"

    # # alice create invoice
    # memo = json.dumps({
    #     "share":True,
    #     "destinations": [
    #         carol_pub,
    #         dave_pub,
    #         erin_pub
    #     ]
    # })

    # # bob creates an invoice (request for payment)
    # invoice = bob.add_invoice(11, 'nicehash')
    # r_hash = invoice.r_hash
    # add_index = invoice.add_index
    # payment_request = invoice.payment_request
    # # print(payment_request)


    # # alice sends payment to bob using payment request
    # alice.send_payment(payment_request)
    # invoice = alice.add_invoice(10000,"test")
    # bob.send_payment(invoice.payment_request)

    # wait a few seconds
    # sleep(10)

    # filter for received payments (invoices) that should be shared
    # this should be an event driven process, possibly with a database
    b_invoices = bob.list_invoices().invoices
    b_payments = bob.list_payments().payments

    # filter out invoices that have already been shared 
    # this is done by checking payments made to each destination 
    # shared payments contain in the memo the hash of original invoice being shared
    unshared_invoices = []
    for invoice in b_invoices: 
      memo = invoice.memo
      policy = get_share_policy(memo)
      if policy:
        print(policy)
        r_hash = invoice.r_has.decode('utf-8')
    

def find_payment(hash,payments):
  for payment in payments:
    pass


if __name__ == '__main__':
    main()
