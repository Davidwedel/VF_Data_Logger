
#!/bin/bash

set -e

UPLOAD_DIR="/srv/ftp/upload"

echo "[*] Installing vsftpd..."

# Detect package manager
if command -v dnf &> /dev/null; then
    sudo dnf install -y vsftpd
elif command -v apt &> /dev/null; then
    sudo apt update && sudo apt install -y vsftpd
else
    echo "Unsupported package manager. Install vsftpd manually."
    exit 1
fi

echo "[*] Creating upload directory..."
sudo mkdir -p "$UPLOAD_DIR"
sudo chmod 777 "$UPLOAD_DIR"
sudo chown ftp:ftp "$UPLOAD_DIR"

echo "[*] Locating vsftpd.conf..."
if [[ -f /etc/vsftpd.conf ]]; then
    CONF_PATH="/etc/vsftpd.conf"
elif [[ -f /etc/vsftpd/vsftpd.conf ]]; then
    CONF_PATH="/etc/vsftpd/vsftpd.conf"
else
    echo "❌ Cannot find vsftpd.conf!"
    exit 1
fi

echo "[*] Backing up original vsftpd.conf..."
sudo cp "$CONF_PATH" "$CONF_PATH.bak"

echo "[*] Writing new vsftpd.conf..."
cat <<EOF | sudo tee "$CONF_PATH" > /dev/null
listen=YES
anonymous_enable=YES
anon_root=/srv/ftp
anon_upload_enable=YES
anon_mkdir_write_enable=YES
write_enable=YES
dirmessage_enable=YES
use_localtime=YES
xferlog_enable=YES
connect_from_port_20=YES
xferlog_std_format=YES
ftpd_banner=Welcome to the anonymous upload FTP server.
listen_ipv6=NO
pam_service_name=vsftpd
seccomp_sandbox=NO
EOF

echo "[*] Opening FTP port in firewall (if applicable)..."
if command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-service=ftp
    sudo firewall-cmd --reload
fi

echo "[*] Restarting vsftpd..."
sudo systemctl restart vsftpd
sudo systemctl enable vsftpd

echo ""
echo "✅ FTP server is running."
echo "📂 Anonymous uploads are allowed at: ftp://<your-ip-address>/upload/"
echo "   (Replace <your-ip-address> with the IP of this machine.)"
