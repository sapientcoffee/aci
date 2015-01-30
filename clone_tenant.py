#!/usr/bin/env python

#==============================================================================
# Title:                tbc
# Description:          This script will list the tenants and based on selection 
#                       clone it including all the EPGs, contracts etc.
# Author:               Rob Edwards (robedwa@cisco.com)
# Date:                 25/01/15
# Version:              0.1
# Dependencies:         acitoolkit
# Credits:              Adapted from the 'datacenter/acitoolkit/multiSite' 
#                       commited by Micheal Smith on the Cisco GitHub repo                     
# Limitations/issues:   Need to finish error checking 
#==============================================================================

import ast
import sys
import logging
from acitoolkit.acisession import Session
import acitoolkit.acitoolkit as ACI
from credentials import *
from prettytable import PrettyTable

logger = logging.getLogger('my-logger')
logger.propagate = False
logging.captureWarnings(True)


def get_json_file_from_apic(choice):
    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    def get_contract_json():
        class_query_url = '/api/node/class/fvTenant.json'
        ret = session.get(class_query_url)
        data = ret.json()['imdata']
        for ap in data:
            dn = ap['fvTenant']['attributes']['dn']
            tenant_name = dn.split('/')[1][3:]
            ap_query_url = '/api/mo/uni/tn-%s.json?rsp-subtree=full&rsp-prop-include=config-only' % (tenant_name)
            ret = session.get(ap_query_url)
            #if tenant_name == from_apic['tenant']:
            if tenant_name == choice:
                return ast.literal_eval(ret.text)['imdata'][0]

    json_file = get_contract_json()
    return json_file

def push_json_to_apic(json_content):
    """
    :param json_content: the json file to be pushed to APIC
    :return: the respond of the push action
    """
    session = Session(to_apic['URL'], to_apic['LOGIN'], to_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    return session.push_to_apic('/api/mo/uni.json', json_content)

def list_tenant():
    session = Session(from_apic['URL'], from_apic['LOGIN'], from_apic['PASSWORD'])
    resp = session.login()
    if not resp.ok:
        print '%% Could not login to APIC'
        sys.exit()

    all_tenant = PrettyTable(["Current Tenant(s)"])
    all_tenant.align["Current Tenant(s)"] = "l" 
    all_tenant.padding_width = 1 

    tenants = ACI.Tenant.get(session)
    for tenant in tenants:
        all_tenant.add_row([tenant.name])
    print all_tenant

def clone():
    
    list_tenant()
    tenant_choice = raw_input("Enter your tenant to clone: ")
    new_tenant = tenant_choice + "-Dev"

    # new menu listing all the tenants
    tenant_extract = get_json_file_from_apic(tenant_choice)
    del tenant_extract['fvTenant']['attributes']['dn']
    #tenant_json_from_github = tenant_extract

    # change tenant name before pushing to another APIC
    #if from_apic['tenant'] != to_apic['tenant']:
    #    tenant_extract['fvTenant']['attributes']['name'] = to_apic['tenant']
    tenant_extract['fvTenant']['attributes']['name'] = new_tenant
    res = push_json_to_apic(tenant_extract)
    #print res


def main_menu():       ## Your menu design here
    main = PrettyTable(["Option", "Description"])
    main.align["Description"] = "l" # Left align city names
    main.padding_width = 1 # One space between column edges and contents (default)
    main.add_row([1,"Clone Tenant to <tenant>-Dev"])
    main.add_row([2,"Copy Tenant config to GitHub"])
    main.add_row([3,"Create Tenant from GitHub"])
    main.add_row([4,"List Tenants"])
    main.add_row([5,"Exit"])
    
    print
    print "Please select an option."
    print "The purpose is to provide options to export or clone tenants and applications within ACI."
    print main


# --- Main ---
loop=True      
  
while loop:          ## While loop which will keep going until loop = False
    main_menu() 
    choice = input("Enter your choice [1-5]: ")
     
    if choice==1:    
        print "Menu 1 has been selected"
        clone()
    elif choice==2:
        print "Menu 2 has been selected - not yet implemented"
        ## You can add your code or functions here
    elif choice==3:
        print "Menu 3 has been selected - not yet implemented"
        ## You can add your code or functions here
    elif choice==4:
        print "Menu 3 has been selected ........."
        list_tenant()
    elif choice==5:
        print "Exiting the script now."
        ## You can add your code or functions here
        loop=False # This will make the while loop to end as not value of loop is set to False
    else:
        # Any integer inputs other than values 1-5 we print an error message
        raw_input("Wrong option selection. Enter any key to try again..")






