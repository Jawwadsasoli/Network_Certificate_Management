import paramiko
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from datetime import datetime
import os

# Configuration
DEVICES = {
    "router1": {"ip": "192.168.1.1", "username": "admin", "password": "password"},
    "switch1": {"ip": "192.168.1.2", "username": "admin", "password": "password"},
}

CERTIFICATE_PATH = "certificate.pem"
PRIVATE_KEY_PATH = "private_key.pem"
DAYS_BEFORE_EXPIRY = 30  # Renew if certificate expires within this many days

# Function to load a certificate
def load_certificate(cert_path):
    """
    Load a certificate from a file.
    """
    with open(cert_path, "rb") as cert_file:
        cert_data = cert_file.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    return cert

# Function to check certificate expiry
def is_certificate_expiring(cert, days_before_expiry):
    """
    Check if a certificate is expiring within the specified number of days.
    """
    expiry_date = cert.not_valid_after
    days_remaining = (expiry_date - datetime.utcnow()).days
    return days_remaining <= days_before_expiry

# Function to deploy certificate to a device
def deploy_certificate(device, cert_path, key_path):
    """
    Deploy a certificate and private key to a network device using SSH.
    """
    ip = device["ip"]
    username = device["username"]
    password = device["password"]

    # Connect to the device
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=username, password=password)

    # Transfer the certificate and private key
    sftp = ssh.open_sftp()
    sftp.put(cert_path, "/path/to/device/certificate.pem")
    sftp.put(key_path, "/path/to/device/private_key.pem")
    sftp.close()

    # Restart the service (e.g., HTTPS) to apply the new certificate
    stdin, stdout, stderr = ssh.exec_command("service https restart")
    print(f"Certificate deployed to {ip}: {stdout.read().decode()}")

    ssh.close()
##Comment
# Main function
def automate_certificate_management():
    """
    Automate certificate management tasks.
    """
    # Load the certificate
    cert = load_certificate(CERTIFICATE_PATH)

    # Check if the certificate is expiring
    if is_certificate_expiring(cert, DAYS_BEFORE_EXPIRY):
        print("Certificate is expiring soon. Renewing...")
        # Replace this with your certificate renewal logic
        # For example, use Let's Encrypt or another CA to issue a new certificate
        # For now, we'll assume a new certificate is already generated and saved

        # Deploy the new certificate to all devices
        for device_name, device in DEVICES.items():
            print(f"Deploying certificate to {device_name} ({device['ip']})...")
            deploy_certificate(device, CERTIFICATE_PATH, PRIVATE_KEY_PATH)
    else:
        print("Certificate is not expiring soon. No action needed.")

# Run the script
if __name__ == "__main__":
    automate_certificate_management()