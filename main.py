import os
import json
import hashlib
import pexpect
import requests
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

client_id = os.getenv('BITWARDEN_CLIENT_ID')
client_secret = os.getenv('BITWARDEN_CLIENT_SECRET')
master_password = os.getenv('BITWARDEN_MASTER_PASSWORD')
skip_accounts = os.getenv('SKIP_ACCOUNTS', '').split(',') if os.getenv('SKIP_ACCOUNTS') else []
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_from_number = os.getenv('TWILIO_FROM_NUMBER')
my_phone_number = os.getenv('MY_PHONE_NUMBER')

print("Checking login status...")
status_output = os.popen('bw status').read()
status = json.loads(status_output)

if status.get('status') == 'unauthenticated':
    print("Logging into Bitwarden...")
    child = pexpect.spawn('bw login --apikey')
    child.expect('client_id:')
    child.sendline(client_id)
    child.expect('client_secret:')
    child.sendline(client_secret)
    child.expect(pexpect.EOF)
    print("Login successful!")
else:
    print(f"Already logged in as {status.get('userEmail', 'unknown user')}")

print("Unlocking vault...")
child = pexpect.spawn('bw unlock')
child.expect('Master password:')
child.sendline(master_password)
child.expect(pexpect.EOF)
output = child.before.decode('utf-8')

session_key = None
for line in output.split('\n'):
    if 'BW_SESSION=' in line:
        session_key = line.split('"')[1]
        break

if not session_key:
    print("Failed to extract session key. Trying alternative method...")
    unlock_output = os.popen(f'echo "{master_password}" | bw unlock --passwordenv BW_MASTER_PASS 2>&1').read()
    for line in unlock_output.split('\n'):
        if 'BW_SESSION=' in line and '"' in line:
            session_key = line.split('"')[1]
            break

if not session_key:
    print("Failed to unlock vault. Output:")
    print(output)
    exit(1)

os.environ['BW_SESSION'] = session_key
print("Vault unlocked successfully!")

print("Fetching vault items...")
items_json = os.popen(f'bw list items --session {session_key}').read()

try:
    items = json.loads(items_json)
except json.JSONDecodeError:
    print(f"Failed to parse vault items. Output: {items_json}")
    exit(1)

breached_passwords = []

for item in items:
    name = item.get('name', 'Unknown')
    
    if name in skip_accounts:
        print(f"Skipping {name}...")
        continue
    
    login = item.get('login')
    if not login:
        continue
    
    password = login.get('password')
    if not password:
        continue
    
    print(f"Checking {name}...")
    
    hashed_pass = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = hashed_pass[:5]
    suffix = hashed_pass[5:]
    
    url = f'https://api.pwnedpasswords.com/range/{prefix}'
    
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Error checking {name}: {e}")
        continue
    
    if response.status_code != 200:
        print(f"Error checking {name}: API returned status {response.status_code}")
        continue
    
    hashes = [line.split(':') for line in response.text.splitlines()]
    
    for hash_suffix, count in hashes:
        if hash_suffix == suffix:
            breached_passwords.append({
                'name': name,
                'count': count
            })
            print(f"⚠️  {name} has been breached {count} times!")
            break

print("\n" + "="*50)
if breached_passwords:
    print(f"Found {len(breached_passwords)} breached password(s):")
    for breach in breached_passwords:
        print(f"  - {breach['name']}: seen {breach['count']} times in breaches")
    
    if twilio_account_sid and twilio_auth_token and twilio_account_sid != 'dummy':
        print("\nSending SMS notification...")
        try:
            client = Client(twilio_account_sid, twilio_auth_token)
            message_body = f"Bitwarden Alert: {len(breached_passwords)} compromised password(s) found!"
            message = client.messages.create(
                body=message_body,
                from_=twilio_from_number,
                to=my_phone_number
            )
            print(f"SMS sent: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")
    else:
        print("\nTwilio not configured - skipping SMS notification")
else:
    print("✓ No breached passwords found!")

print("="*50)

os.popen('bw lock')
print("\nVault locked. Done!")

