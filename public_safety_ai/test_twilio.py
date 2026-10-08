import os
from twilio.rest import Client

# Direct test credentials
sid = "AC1eaf0218d9df7574322ea8ec8009bfcc"
token = "33674af531291ecf55b382a3c3fbd9af"
from_num = "whatsapp:+14155238886"
to_num = "whatsapp:+918826202125"

try:
    client = Client(sid, token)
    message = client.messages.create(
        body="🚨 I4C Alert: Test dispatch to Cyber Cell Duty Officer successful!",
        from_=from_num,
        to=to_num
    )
    print(f"✅ Success! Message SID: {message.sid}")
    print(f"Status: {message.status}")
except Exception as e:
    print(f"❌ Twilio Error Details: {e}")