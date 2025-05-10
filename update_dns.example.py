import os
import requests
from dotenv import load_dotenv

# Load environment variables from ~/.env
load_dotenv(dotenv_path=os.path.expanduser('~/.env'))

# Load API credentials
API_KEY = os.getenv("PORKBUN_API_KEY")
SECRET_API_KEY = os.getenv("PORKBUN_SECRET_API_KEY")
DOMAIN = os.getenv("DOMAIN_NAME")
MAIL_SERVER_IP = os.getenv("MAIL_SERVER_IP")

# Porkbun API base URL
API_BASE = "https://porkbun.com/api/json/v3"

# Define the records you want to create
dns_records = [
    {
        "type": "A",
        "name": "mail",
        "content": MAIL_SERVER_IP,
        "ttl": 300
    },
    {
        "type": "MX",
        "name": "@",
        "content": f"mail.{DOMAIN}",
        "priority": 10,
        "ttl": 300
    },
    {
        "type": "TXT",
        "name": "@",
        "content": "v=spf1 mx ~all",
        "ttl": 300
    },
    {
        "type": "TXT",
        "name": "_dmarc",
        "content": "v=DMARC1; p=none; rua=mailto:dmarc@{}".format(DOMAIN),
        "ttl": 300
    }
]

def create_dns_record(record):
    url = f"{API_BASE}/dns/create/{DOMAIN}"
    payload = {
        "apikey": API_KEY,
        "secretapikey": SECRET_API_KEY,
        **record
    }
    response = requests.post(url, json=payload)
    result = response.json()
    print(f"Creating {record['type']} record for {record['name']}.{DOMAIN}: {result['status']}")

if __name__ == "__main__":
    for record in dns_records:
        create_dns_record(record)