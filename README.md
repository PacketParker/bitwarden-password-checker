# Bitwarden Password Checker

A Python script that checks passwords stored in your Bitwarden vault against the [Have I Been Pwned](https://haveibeenpwned.com/) database to identify compromised passwords. If breached passwords are found, the script can send you a text message alert via Twilio.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Privacy & Security](#privacy--security)
- [Automated Checks](#automated-checks)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Features

- 🔐 Checks Bitwarden vault passwords against the Have I Been Pwned database
- 🛡️ Uses k-Anonymity principle for secure password checking (your passwords are never sent to external services)
- 📱 Optional SMS alerts via Twilio when compromised passwords are found
- ⚙️ Skip specific vault entries you don't want to check
- 🧹 Automatically locks your vault after checking

## Prerequisites

- **Operating System**: UNIX-based systems (Linux, macOS) - Windows support is limited due to pexpect dependency
- **Python**: 3.6 or higher
- **Bitwarden CLI**: Must be installed and accessible in your PATH
- **Internet Connection**: Required to check against HIBP API

## Installation

1. **Clone or download this repository:**
    ```bash
    git clone https://github.com/Ahmed9190/bitwarden-password-checker.git
    cd bitwarden-password-checker
    ```

2. **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # or
    venv\Scripts\activate     # On Windows (if supported)
    ```

3. **Install required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    
    If no requirements.txt exists, install manually:
    ```bash
    pip install pexpect twilio python-dotenv requests
    ```

4. **Install Bitwarden CLI:**
    - Follow the [official Bitwarden CLI installation guide](https://bitwarden.com/help/cli/)
    - Verify installation: `bw --version`

## Configuration

1. **Create your environment file:**
    ```bash
    cp .env.example .env
    ```

2. **Configure your `.env` file with the following variables:**

    | Variable | Description | Required |
    |----------|-------------|----------|
    | `BITWARDEN_CLIENT_ID` | Your Bitwarden API client ID | Yes |
    | `BITWARDEN_CLIENT_SECRET` | Your Bitwarden API client secret | Yes |
    | `BITWARDEN_MASTER_PASSWORD` | Your Bitwarden master password | Yes |
    | `SKIP_ACCOUNTS` | Comma-separated list of vault item names to skip (optional) | No |
    | `TWILIO_ACCOUNT_SID` | Twilio Account SID for SMS alerts (optional) | No |
    | `TWILIO_AUTH_TOKEN` | Twilio Auth Token for SMS alerts (optional) | No |
    | `TWILIO_FROM_NUMBER` | Twilio phone number to send from (optional) | No |
    | `MY_PHONE_NUMBER` | Your phone number to receive alerts (optional) | No |

### Getting Bitwarden API Credentials

1. Log in to your Bitwarden web vault at [vault.bitwarden.com](https://vault.bitwarden.com)
2. Go to **Settings** > **My Account** > **App API Key**
3. Click **Create Account API Key**
4. Copy the Client ID and Client Secret to your `.env` file

### Optional: Configure SMS Alerts with Twilio

Sign up for a [Twilio account](https://www.twilio.com/try-twilio) and get your credentials from the Twilio Console.

## Usage

1. **Ensure your virtual environment is activated:**
    ```bash
    source venv/bin/activate
    ```

2. **Run the script:**
    ```bash
    python main.py
    ```

3. **View the results:**
    - The script will check each password in your vault (except skipped items)
    - Compromised passwords will be reported with the number of times they've been seen in breaches
    - If configured, SMS alerts will be sent with the summary

### Example Output
```
Checking login status...
Already logged in as user@example.com
Unlocking vault...
Vault unlocked successfully!
Fetching vault items...
Checking Gmail...
Checking Bank Account...
⚠️  Bank Account has been breached 1250 times!

==================================================
Found 1 breached password(s):
  - Bank Account: seen 1250 times in breaches

Sending SMS notification...
SMS sent: SMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
==================================================

Vault locked. Done!
```

## Privacy & Security

This tool implements the k-Anonymity principle to protect your password privacy:

1. Your actual passwords are never sent to external services
2. Passwords are hashed locally using SHA-1
3. Only the first 5 characters of the hash are sent to the Have I Been Pwned API
4. The API returns a list of hashes that match those 5 characters
5. The comparison with your full hash happens locally
6. For more information about this approach, see:
   - [Have I Been Pwned API Documentation](https://haveibeenpwned.com/API/v3#SearchingPwnedPasswordsByRange)
   - [Cloudflare's explanation of k-Anonymity](https://blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity/)

### Security Best Practices

- Store your `.env` file securely and never commit it to version control
- Use a strong master password for your Bitwarden account
- Regularly update your compromised passwords
- Consider using this tool in a secure environment

## Automated Checks

You can set up regular automated checks using cron jobs:

1. **Open your crontab:**
    ```bash
    crontab -e
    ```

2. **Add a cron job (example runs daily at 3 AM):**
    ```bash
    0 3 * * * cd /path/to/bitwarden-password-checker && source venv/bin/activate && python main.py >> /path/to/logfile.log 2>&1
    ```

3. **For weekly checks (Sundays at 3 AM):**
    ```bash
    0 3 * * 0 cd /path/to/bitwarden-password-checker && source venv/bin/activate && python main.py >> /path/to/logfile.log 2>&1
    ```

## Troubleshooting

### Common Issues

**"Failed to unlock vault" or "Failed to extract session key"**
- Ensure your Bitwarden CLI is properly installed and accessible
- Verify your master password is correct in the `.env` file
- Try logging in manually with `bw login --apikey` first

**"ModuleNotFoundError" or dependency issues**
- Make sure you've activated your virtual environment
- Install dependencies with `pip install pexpect twilio python-dotenv requests`

**"Command 'bw' not found"**
- Ensure Bitwarden CLI is installed and added to your PATH
- Test with `bw --version` in your terminal

**"Failed to authenticate with Twilio"**
- Verify your Twilio credentials in the `.env` file
- Check that you have a valid Twilio account and purchased/verified phone numbers

### Getting Help

If you encounter issues:
1. Verify all environment variables are correctly set
2. Check that the Bitwarden CLI is working independently
3. Review the [Bitwarden CLI documentation](https://bitwarden.com/help/cli/)
4. Open an issue in this repository if you encounter bugs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Unlicense - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is provided for personal security checking purposes. Use responsibly and ensure you have proper authorization to access any accounts being checked. Always follow security best practices and regularly update your passwords.
