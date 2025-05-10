# Headless, And Fully Automatable Setup 

*for deploying a mailcow mail server on aws ec2 using terraform and ansible*

---

### Pre-Requisites

- No manual UI interaction
- Full automation via code
- Programmatic management of mailboxes and domains
- Programmatic access to emails

---

## Overview of the Stack

- Infrastructure Provisioning: Terraform
- Server Configuration: Ansible
- Mail Server: Mailcow: Dockerized
- DNS Management: Porkbun API (as previously discussed)
- Email Access: IMAP (e.g., via Python’s imaplib or imapclient)
- Mailbox Management: Mailcow REST API

---

## Project Structure

mailcow-automation/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── ansible/
│   ├── inventory.ini
│   └── playbook.yml
├── .env
└── README.md


---

## Step-by-Step Setup

1. Provision EC2 Instance with Terraform

terraform/main.tf:

```tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_key_pair" "mailcow_key" {
  key_name   = "mailcow-key"
  public_key = file("~/.ssh/id_rsa.pub")  # Ensure this path is correct
}

resource "aws_security_group" "mailcow_sg" {
  name        = "mailcow-sg"
  description = "Allow ports for Mailcow"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Add other necessary ports (e.g., 25, 587, 993) as needed

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "mailcow" {
  ami                    = "ami-0abcdef1234567890"  # Replace with a valid Ubuntu AMI ID
  instance_type          = "t3a.medium"
  key_name               = aws_key_pair.mailcow_key.key_name
  vpc_security_group_ids = [aws_security_group.mailcow_sg.id]

  provisioner "remote-exec" {
    inline = [
      "sudo apt update && sudo apt install -y python3 python3-pip"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file("~/.ssh/id_rsa")  # Ensure this path is correct
      host        = self.public_ip
    }
  }

  tags = {
    Name = "MailcowServer"
  }
}

output "mailcow_public_ip" {
  value = aws_instance.mailcow.public_ip
}
```

> ***Note: Replace the AMI ID with a valid Ubuntu AMI for your region.***

---

2. Configure Server with Ansible

ansible/inventory.ini:

[mailcow]
<MAILCOW_PUBLIC_IP> ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa

ansible/playbook.yml:

```yml
- hosts: mailcow
  become: yes
  vars:
    mailcow_hostname: "mail.yourdomain.com"
    mailcow_timezone: "America/New_York"
    mailcow_install_path: "/opt/mailcow-dockerized"
  tasks:
    - name: Install dependencies
      apt:
        name: ['git', 'docker.io', 'docker-compose']
        state: present
        update_cache: yes

    - name: Clone Mailcow repository
      git:
        repo: 'https://github.com/mailcow/mailcow-dockerized'
        dest: "{{ mailcow_install_path }}"
        version: master

    - name: Copy Mailcow configuration
      template:
        src: mailcow.env.j2
        dest: "{{ mailcow_install_path }}/.env"

    - name: Start Mailcow
      shell: |
        cd {{ mailcow_install_path }}
        docker-compose pull
        docker-compose up -d
```

ansible/templates/mailcow.env.j2:

```
MAILCOW_HOSTNAME={{ mailcow_hostname }}
MAILCOW_TIMEZONE={{ mailcow_timezone }}
```

---

3. Automate DNS Configuration with Porkbun API

Integrate `/mail/update_dns.py` to set up DNS records via Porkbun’s API. 

Ensure that the script is executed *after* the EC2 instance is provisioned and Mailcow is configured.

---

4. Manage Mailboxes Programmatically via Mailcow API

Mailcow provides a RESTful API to manage domains, mailboxes, and more.

*Example: Create a new mailbox using Python.*

```py
import requests

API_KEY = 'your_mailcow_api_key'
BASE_URL = 'https://mail.yourdomain.com/api/v1'

headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

data = {
    "local_part": "user",
    "domain": "yourdomain.com",
    "password": "securepassword",
    "active": 1
}

response = requests.post(f"{BASE_URL}/add/mailbox", headers=headers, json=data)

if response.status_code == 200:
    print("Mailbox created successfully.")
else:
    print(f"Error: {response.text}")
```

---

5. Access Emails Programmatically via IMAP

Use Python’s imaplib or imapclient to access and process emails.

Example:

```py
import imaplib
import email

IMAP_SERVER = 'mail.yourdomain.com'
EMAIL_ACCOUNT = 'user@yourdomain.com'
PASSWORD = 'securepassword'

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_ACCOUNT, PASSWORD)
mail.select('inbox')

status, data = mail.search(None, 'ALL')
mail_ids = data[0].split()

for num in mail_ids:
    status, msg_data = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(msg_data[0][1])
    print(f"From: {msg['From']}")
    print(f"Subject: {msg['Subject']}")
```

---

Testing & Validation

After deployment:
- DNS: Verify MX, SPF, DKIM, and DMARC records using tools like MXToolbox.
- Mailcow: Access the Mailcow admin panel at https://mail.yourdomain.com to ensure services are running.
- Email Sending/Receiving: Test sending and receiving emails using the created mailboxes.

---

Additional Tips

- Data Persistence: Ensure that Mailcow’s Docker volumes are backed up or stored on persistent storage to prevent data loss during instance recreation.
- Security: Regularly update your system and Docker images. Implement firewall rules to restrict unnecessary access.
- Monitoring: Consider integrating monitoring tools to keep an eye on server health and email queues.

---

Would you like a GitHub repository template with this setup or further assistance in customizing any part of this deployment?