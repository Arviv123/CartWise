# CartWise Pro - Deployment Checklist
## רשימת בדיקות לפני הפצה

---

## ✅ Pre-Deployment Checklist

### 1. System Requirements ✓
- [ ] Raspberry Pi 4 (or equivalent) with Raspberry Pi OS
- [ ] Python 3.8+ installed
- [ ] USB-RS485 adapter connected
- [ ] Lock controller with micro-switches installed
- [ ] Network connectivity (WiFi or Ethernet)
- [ ] Touchscreen display (optional but recommended)

### 2. Software Installation ✓
```bash
# Navigate to project directory
cd CartWise-Pro

# Install dependencies
pip3 install -r requirements.txt

# Verify installation
python3 -c "import fastapi, uvicorn, serial, requests; print('✓ All packages installed')"
```

### 3. Configuration ✓
```bash
# Copy environment template
cp config/.env.example config/.env

# Edit configuration
nano config/.env
```

**Required settings in `.env`:**
```env
# SMS Credentials (Get from Inforu)
INFORU_USERNAME=your_actual_username
INFORU_PASSWORD=your_actual_password

# Hardware Setup
SERIAL_PORT=/dev/ttyUSB0        # Check with: ls -l /dev/ttyUSB*
BAUD_RATE=9600

# Server Configuration
HOST=0.0.0.0                    # Listen on all interfaces
PORT=8001                       # Default port

# OTP Settings
OTP_LENGTH=4
OTP_EXPIRATION_MINUTES=5
```

### 4. Hardware Connection Test ✓

**Step 1: Identify RS485 Device**
```bash
# List USB serial devices
ls -l /dev/ttyUSB*

# Expected output:
# /dev/ttyUSB0
```

**Step 2: Set Permissions**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Set permissions (temporary)
sudo chmod 666 /dev/ttyUSB0

# Logout and login for group changes to take effect
```

**Step 3: Test Serial Communication**
```bash
# Using Python
python3 << EOF
import serial
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
print(f"✓ Connected to {ser.name}")
ser.close()
EOF
```

### 5. SMS Provider Test ✓

**Test Inforu API:**
```bash
# Create test script
cat > test_sms.py << 'EOF'
import sys
sys.path.append('src')
from sms.inforu import InforuSMSProvider
import os
from dotenv import load_dotenv

load_dotenv('config/.env')

provider = InforuSMSProvider(
    username=os.getenv('INFORU_USERNAME'),
    password=os.getenv('INFORU_PASSWORD')
)

# Test SMS (replace with your phone number)
response = provider.send_sms('0501234567', 'Test message from CartWise Pro')
print(f"SMS sent: {response.success}")
print(f"Message: {response.message}")
EOF

# Run test
python3 test_sms.py

# Clean up
rm test_sms.py
```

### 6. System Test ✓

**Start the server:**
```bash
python3 src/api/main.py
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

**Test endpoints:**
```bash
# In a new terminal:

# 1. Health check
curl http://localhost:8001/health

# Expected: {"status":"healthy","timestamp":"..."}

# 2. Get available carts
curl http://localhost:8001/carts/available

# Expected: [{"cart_id":1,"status":"available",...},...]

# 3. API documentation
# Open browser: http://localhost:8001/docs
```

### 7. Full Flow Test ✓

**Test complete user journey:**

1. **Open customer interface**
   - Browser: `http://localhost:8001`
   - Or on touchscreen: `http://[raspberry-pi-ip]:8001`

2. **Request OTP**
   - Enter valid Israeli phone number (05XXXXXXXX)
   - Click "קבל קוד אימות"
   - Check phone for SMS

3. **Verify OTP**
   - Enter 4-digit code
   - Click "אמת קוד"

4. **Cart Assignment**
   - System should assign cart
   - Lock should unlock (listen for click)
   - Confirmation SMS received

5. **Return Cart**
   - Place cart back in position
   - Micro-switch should trigger
   - Lock should auto-lock
   - Cart marked as available

### 8. Production Deployment ✓

**Create systemd service:**
```bash
# Create service file
sudo nano /etc/systemd/system/cartwise.service
```

**Service configuration:**
```ini
[Unit]
Description=CartWise Pro - Smart Cart Management
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/CartWise-Pro
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /home/pi/CartWise-Pro/src/api/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable cartwise

# Start service
sudo systemctl start cartwise

# Check status
sudo systemctl status cartwise
```

**View logs:**
```bash
# Real-time logs
sudo journalctl -u cartwise -f

# Last 100 lines
sudo journalctl -u cartwise -n 100
```

### 9. Security Hardening ✓

**Firewall configuration:**
```bash
# Install UFW
sudo apt install ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow CartWise port
sudo ufw allow 8001/tcp

# Enable firewall
sudo ufw enable
```

**HTTPS Setup (Optional but recommended):**
```bash
# Install nginx
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/cartwise
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 10. Monitoring Setup ✓

**Create monitoring script:**
```bash
cat > ~/monitor_cartwise.sh << 'EOF'
#!/bin/bash

# Check if service is running
if systemctl is-active --quiet cartwise; then
    echo "✓ CartWise is running"
else
    echo "✗ CartWise is NOT running!"
    sudo systemctl start cartwise
fi

# Check API health
HEALTH=$(curl -s http://localhost:8001/health | grep -o "healthy")
if [ "$HEALTH" = "healthy" ]; then
    echo "✓ API is healthy"
else
    echo "✗ API health check failed!"
fi
EOF

chmod +x ~/monitor_cartwise.sh

# Add to crontab (runs every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * ~/monitor_cartwise.sh >> ~/cartwise_monitor.log 2>&1") | crontab -
```

---

## 🔍 Troubleshooting

### Issue: "Permission denied" on /dev/ttyUSB0
**Solution:**
```bash
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyUSB0
# Then logout and login
```

### Issue: "Module not found"
**Solution:**
```bash
pip3 install -r requirements.txt --upgrade
```

### Issue: SMS not sending
**Solution:**
1. Check Inforu credentials in `.env`
2. Verify phone number format (05XXXXXXXX)
3. Check Inforu account credit
4. Test with `test_sms.py` script

### Issue: Port 8001 already in use
**Solution:**
```bash
# Find process
sudo lsof -ti:8001

# Kill process
sudo kill $(sudo lsof -ti:8001)

# Or change port in .env
```

### Issue: Lock not responding
**Solution:**
1. Check USB connection: `ls -l /dev/ttyUSB*`
2. Verify baud rate in `.env` (should be 9600)
3. Test with manual command
4. Check lock controller power

### Issue: Micro-switch not detecting
**Solution:**
1. Test switch with multimeter
2. Check wiring connections
3. Verify controller firmware
4. Test with status query command

---

## 📊 Performance Benchmarks

**Expected metrics:**
- API response time: < 50ms
- Lock control: < 100ms
- SMS delivery: 1-3 seconds
- OTP generation: < 10ms
- Concurrent users: 100+

**Test with:**
```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API performance
ab -n 100 -c 10 http://localhost:8001/health
```

---

## 📱 Mobile Access

**Access from phone/tablet:**
1. Find Raspberry Pi IP: `hostname -I`
2. Open browser on mobile device
3. Navigate to: `http://[raspberry-pi-ip]:8001`
4. Bookmark for easy access

**Create QR code for easy access:**
```bash
# Install qrencode
sudo apt install qrencode

# Generate QR code
qrencode -o cartwise_qr.png "http://$(hostname -I | awk '{print $1}'):8001"

# Display QR code
feh cartwise_qr.png
```

---

## 🎯 Success Criteria

System is ready for production when:
- ✅ All tests pass
- ✅ Service auto-starts on boot
- ✅ SMS messages delivered successfully
- ✅ Locks respond to commands
- ✅ Micro-switches detect cart return
- ✅ Customer interface loads properly
- ✅ Logs show no errors
- ✅ Monitoring is active

---

## 📞 Support Contacts

**Technical Issues:**
- Email: support@cartwise.com
- Phone: 050-XXXXXXX
- Hours: 9:00-17:00 IST

**Emergency (Production Down):**
- Phone: 050-XXXXXXX (24/7)

---

## 📝 Maintenance Schedule

**Daily:**
- Check system logs
- Verify service status
- Monitor available carts

**Weekly:**
- Review SMS delivery rate
- Check lock operation
- Update statistics

**Monthly:**
- Update dependencies
- Review security logs
- Backup configuration

**Quarterly:**
- Test all locks
- Verify micro-switches
- Hardware inspection

---

## 🔐 Backup & Recovery

**Backup configuration:**
```bash
# Create backup
tar -czf cartwise_backup_$(date +%Y%m%d).tar.gz \
    CartWise-Pro/config/.env \
    CartWise-Pro/data/

# Restore from backup
tar -xzf cartwise_backup_YYYYMMDD.tar.gz
```

**Recovery procedure:**
1. Stop service: `sudo systemctl stop cartwise`
2. Restore files from backup
3. Verify configuration
4. Start service: `sudo systemctl start cartwise`
5. Test all functionality

---

## ✅ Final Checklist

Before going live:
- [ ] All hardware connected and tested
- [ ] SMS provider configured and tested
- [ ] Service running and auto-starting
- [ ] Firewall configured
- [ ] Monitoring active
- [ ] Logs being written
- [ ] Customer interface accessible
- [ ] Full user flow tested
- [ ] Emergency contacts available
- [ ] Backup strategy in place
- [ ] Team trained on system
- [ ] Documentation reviewed

---

**Deployment Date:** __________
**Deployed By:** __________
**System Status:** __________
**Notes:** __________

---

**🎉 System Ready for Production! 🎉**

---

*Good luck with your deployment! For any issues, refer to the troubleshooting section or contact support.*
