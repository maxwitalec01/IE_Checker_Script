import csv
import gspread
import whmcspy
import urllib3
from dotenv import load_dotenv
import os
from datetime import datetime
import json
import datetime

# Disabling SSL warnings and loading environment variables
urllib3.disable_warnings()
load_dotenv()


API_URL = os.getenv('MANAGE_WEBWORLD_API'),
API_IDENTIFIER = os.getenv('MANAGE_WEBWORLD_IDENTIFIER'),
API_SECRET = os.getenv('MANAGE_WEBWORLD_SECRET')

# Function to get current timestamp
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

whmcs = whmcspy.WHMCS(
    'https://manage.webworld.ie/includes/api.php',
    API_IDENTIFIER,
    API_SECRET
)

#domain_check = str(input("Enter Domain: "))

# Assuming 'invoices' is your list of invoice dictionaries
def parse_date(invoice):
    try:
        return datetime.datetime.strptime(invoice['date'], "%Y-%m-%d")
    except ValueError:
        # If the date format is incorrect or missing, set a default minimum date
        return datetime.datetime.min


GetClientsDomains = whmcs.call(
    'GetClientsDomains',
    domain="layouts.ie"
)

# response is dict, get USER ID from this dict
userid = GetClientsDomains["domains"]["domain"][0]["userid"]
print(userid)

GetInvoices = whmcs.call(
    'GetInvoices',
    userid=userid
)


user_invoices = GetInvoices["invoices"]["invoice"]
# GPT // SORTS THE DICTIONARY BY NEWEST FIRST
sorted_invoices = sorted(user_invoices, key=parse_date, reverse=True)
print(sorted_invoices)

# Initalise the flag to break out of the loop
found = False

for invoice in sorted_invoices:
    user_invoice = invoice["id"]

    GetSpecificInvoice = whmcs.call(
        'GetInvoice',
        invoiceid=user_invoice
    )

    # NEED TO IMPLEMENT LOOP FOR THE [0] TO GO THROUGH PRODUCTS IN THE INVOICE
    specific_invoice_products = GetSpecificInvoice["items"]["item"] # [0]["description"].split(" ")
    for x in specific_invoice_products:
        invoice_product = x["description"]
        print(invoice_product)
        if "Domain Renewal - " + "layouts.ie" in invoice_product:
            print("True")
            print(GetSpecificInvoice["status"])
            # set the flag to True
            found = True
        else:
            print("False")
    
    if found:
        break

            

    # for products in specific_invoice_products:
    #     for product in products["description"]:
    #         print(product)
    #     #print(specific_invoice_products)

    # # REPLACE ux-heuristictesting.ie WITH DOMAIN SEARCHED FOR
    # if "ux-heuristictesting.ie" in specific_invoice_products:
    #     # IF TRUE BREAK OUT OF LOOP
    #     print("True")
    #     print(user_invoice)
    #     GetSpecificInvoice["status"]
    #     break
    # else:
    #     # LOOP AGAIn
    #     print("False")
