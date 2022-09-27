# Bitwarden Password Checker (UNIX Systems ONLY)

## Overview
Uses the Bitwarden CLI tool (available [here](https://bitwarden.com/help/cli/)), the Twilio API, and the HaveIBeenPwned API in order to check the passwords in your vault against the SHA-1 hashes of compromised passwords. If a compromised password is found, it alerts you with a text message.
<br>
## Setup
In order to setup everything, you must enter all of the necessary information into a .env file (Format can be found in `.env.example` file). Please note, the `SKIP_ACCOUNTS` field should be a list of comma seperated entry names (EX: Google, Youtube, etc.) If you would not like to skip any accounts in your vault, simply leave this field blank, but do NOT delete the whole field.

Install the required dependencies (pexpect, twilio, python-dotenv, requests)
<br>
<br>
## Side Notes
You can easily setup this script to run on a cron job, that way you can start it and leave it, and have the script periodically check and alert you for breached passwords.
<br><br>
Your passwords are NEVER exposed to the public HaveIBeenPwned API. Your passwords are taken in plaint text from your Bitwarden vault, using the CLI tool, and then hashed into their SHA-1 hashes. After this, the first 5 characters of the hash are sent to the API, which returns are matching entries. This list will then check against the full hashes which are stored in a list. This method is called k-Anonymity, you can read more about it below

    https://haveibeenpwned.com/API/v3#SearchingPwnedPasswordsByRange
    https://blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity/

Regarding the dependency of a UNIX system, this is because of the dependency of the pexpect module, which is used to login to your Bitwarden account with your API credentials. The functions which are used are only available for use on UNIX based systems.
<br>
<br>
Feel free you fork this project or download the code and use it for your own needs. Happy coding!
