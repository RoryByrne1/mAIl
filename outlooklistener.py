import imaplib
import email
from email.header import decode_header

# Account credentials
username = "braawlerz@gmail.com"
password = "braawl*s"

# Connect to the server
mail = imaplib.IMAP4_SSL("imap.gmail.com")

# Login to your account
mail.login(username, password)

# Select the mailbox you want to use
mail.select("inbox")

# Search for all emails in the inbox
status, messages = mail.search(None, "ALL")

# Convert messages to a list of email IDs
email_ids = messages[0].split()

# Get the first three emails
for i in range(3):
    # Fetch the email by ID
    res, msg = mail.fetch(email_ids[i], "(RFC822)")
    
    for response in msg:
        if isinstance(response, tuple):
            # Parse the email content
            msg = email.message_from_bytes(response[1])
            # Decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # If it's a bytes type, decode to str
                subject = subject.decode(encoding if encoding else "utf-8")
            # Decode email sender
            from_ = msg.get("From")
            print("Subject:", subject)
            print("From:", from_)
            print()

            # If the email message is multipart
            if msg.is_multipart():
                # Iterate over email parts
                for part in msg.walk():
                    # Extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    try:
                        # Get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass

                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # Print text/plain emails and skip attachments
                        print(body)
            else:
                # Extract content type of email
                content_type = msg.get_content_type()

                # Get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # Print only text email parts
                    print(body)

# Close the connection and logout
mail.close()
mail.logout()