import csv
import gspread
import whmcspy
import urllib3
from dotenv import load_dotenv
import os
from datetime import datetime

# Initialize Google Sheets API
gc = gspread.service_account(filename="creds.json")
sh1 = gc.open("IEDR Issue").worksheet("IE_Script Input")
sh2 = gc.open("IEDR Issue").worksheet("IE_Script Output")

# Disabling SSL warnings and loading environment variables
urllib3.disable_warnings()
load_dotenv()

# Define the credentials for each system
systems = {
    "WW": {"api_url": os.getenv('MANAGE_WEBWORLD_API'), "api_identifier": os.getenv('MANAGE_WEBWORLD_IDENTIFIER'), "api_secret": os.getenv('MANAGE_WEBWORLD_SECRET')},
    "WH": {"api_url": os.getenv('MANAGE_WEBHOST_API'), "api_identifier": os.getenv('MANAGE_WEBHOST_IDENTIFIER'), "api_secret": os.getenv('MANAGE_WEBHOST_SECRET')},
    "HI": {"api_url": os.getenv('MANAGE_MYACCOUNT_API'), "api_identifier": os.getenv('MANAGE_MYACCOUNT_IDENTIFIER'), "api_secret": os.getenv('MANAGE_MYACCOUNT_SECRET')}
}

# Function to get the last row number in the sheet
def get_last_row(sheet):
    str_list = list(filter(None, sheet.col_values(1)))  # Read first column and filter out empty cells
    return len(str_list)

# Function to get current timestamp
def get_current_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Read domains from Sheet1
domains_to_check = sh1.col_values(1)  # Assuming domains are in the first column of Sheet1

# Function to check domain status and invoice
def check_domain_status_and_invoice(domain, systems):
    for system_name, credentials in systems.items():
        whmcs = whmcspy.WHMCS(
            credentials["api_url"],
            credentials["api_identifier"],
            credentials["api_secret"]
        )

        # Make the API call
        domain_info_response = whmcs.call('GetClientsDomains', domain=domain)

        # Check if the domain was found
        if (domain_info_response and 'domains' in domain_info_response and 'domain' in domain_info_response['domains'] and isinstance(domain_info_response['domains']['domain'], list) and domain_info_response['domains']['domain']):
            domain_info = domain_info_response["domains"]["domain"][0]
            domain_status = domain_info["status"].capitalize()
            dar_status = domain_info.get('donotrenew', '1')
            status_prefix = "DAR " if dar_status else ""

            # Get USER ID to check invoice details
            userid = domain_info["userid"]
            try:
                user_invoices = whmcs.call('GetInvoices', userid=userid, limitnum=50, order="desc")["invoices"]["invoice"]
            except:
                "Error Line 61"
                break


            for invoice in user_invoices:
                specific_invoice = whmcs.call('GetInvoice', invoiceid=invoice["id"])
                for item in specific_invoice["items"]["item"]:
                    if f"Domain Renewal - {domain}" in item["description"]:
                        invoice_status = specific_invoice["status"]
                        invoice_number = invoice["id"]
                        return f"{status_prefix}{domain_status}", system_name, invoice_status, invoice_number

    return "Domain not found in any database", "Not found", "Not found", "Not found"

# Update the Google Sheet with domain and invoice details
for domain in domains_to_check:
    domain_status, system_name, invoice_status, invoice_number = check_domain_status_and_invoice(domain, systems)
    next_row = get_last_row(sh2) + 1
    timestamp = get_current_timestamp()
    sh2.update(f"A{next_row}:F{next_row}", [[domain, domain_status, system_name, invoice_status, invoice_number, timestamp]])

print("Sheet2 updated with domain and invoice details.")