import imaplib, email
from email.header import decode_header

imap_host = "mail.yourdomain.com"
username = "admin@yourdomain.com"
password = "your_password"

mail = imaplib.IMAP4_SSL(imap_host)
mail.login(username, password)
mail.select("inbox")

def get_msgs(mail):
	result, data = mail.search(None, "ALL")
	for num in data[0].split():
		result, msg_data = mail.fetch(num, "(RFC822)")
		raw_email = msg_data[0][1]
		msg = email.message_from_bytes(raw_email)
		print(f"From: {msg['From']}")
		print(f"Subject: {decode_header(msg['Subject'])[0][0]}")
	return msg