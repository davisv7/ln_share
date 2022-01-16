from lndgrpc import LNDClient
import lndgrpc.rpc_pb2 as ln
import configparser
import json
import time
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
    with open('shares.yaml') as f:
        conf = yaml.safe_load(f)
        for key in conf.keys():
            if key in memo:
                return conf[key]
        return False


def check_invoice_paid():
    pass


def make_fake_data(alice, bob):
    # bob creates an invoice (request for payment)
    invoice = bob.add_invoice(11, 'nicehash')
    r_hash = invoice.r_hash
    add_index = invoice.add_index
    payment_request = invoice.payment_request
    # print(payment_request)

    # alice sends payment to bob using payment request
    alice.send_payment(payment_request)

    invoice = alice.add_invoice(10000, "test")
    bob.send_payment(invoice.payment_request)


def main():
    config = configparser.ConfigParser()
    config.read("project.config")

    alice = create_node_obj(config, "alice")
    bob = create_node_obj(config, "bob")
    # carol_pub = "02aa93525d98c65c1b1bbe6486fc3b5918657ba8664065906c356c14288da78621"
    # dave_pub = "0283b2f17ef004426f545a9b84c86e7edca548ef5029218fdce9b8bd2979aea83b"
    # erin_pub = "0227f7850fcd6d33b8dbe589232619e6b17fc8b22cbcf9a136bf17f93c0bbd3c24"

    # make_fake_data(alice, bob)

    # filter Bobs received payments (invoices) for those that should be shared
    # this should be an event driven process, possibly with a database
    b_invoices = bob.list_invoices().invoices
    b_payments = bob.list_payments().payments

    unshared_invoices = []
    for invoice in b_invoices:
        memo = invoice.memo
        policy = get_share_policy(memo)
        if policy:
            print(policy)
            if not invoice_has_been_shared(invoice, b_payments):
                # payments were not found, so share the invoice
                share_invoice(bob, invoice)


def find_payment(hash, payments):
    for payment in payments:
        pass


def share_invoice(node, invoice):
    memo = invoice.memo
    amt_paid = invoice.amt_paid_sat
    memo_json = json.loads(memo)
    shares = memo_json["shares"]  # TODO: add an assertion to make sure the shares add up to 1.0

    # create the payment request on the destinations behalf
    for pub_key, share in shares.items():
        sat_share = int(amt_paid * share)  # may lose one sat
        temp_invoice = ln.Invoice(memo="", value=sat_share, expiry=3600, creation_data=int(time.time()))
        payment_request = temp_invoice.payment_request
        node.send_payment(payment_request)


# filter out invoices that have already been shared
# this is done by checking payments made to each destination
# shared payments contain in the memo the hash of original invoice being shared
def invoice_has_been_shared(invoice, payments):
    r_hash = invoice.r_has.decode('utf-8')
    for payment in payments:
        pass
    return False


if __name__ == '__main__':
    main()
