# SSL Setup with Let's Encrypt (Certbot)

## Overview
Setting up SSL/HTTPS for all applications using Let's Encrypt certificates for trusted, browser-compatible HTTPS.

## Prerequisites
- Ubuntu 22.04+ server
- Domain names already pointing to the server:
  - `hosting.remoteds.us`
  - `cigars.remoteds.us`
  - `tobacco.remoteds.us`
- Nginx already installed and configured

## Certbot Installation and Setup

### 1. Install Certbot and Nginx Plugin
```bash
# Update package list
sudo apt update

# Install certbot with nginx plugin
sudo apt install -y certbot python3-certbot-nginx

# Verify installation
certbot --version
```

### 2. Configure Nginx for Certbot
Ensure your Nginx configuration files have proper `server_name` directives:

```nginx
# /etc/nginx/sites-available/hosting.remoteds.us
server {
    listen 80;
    server_name hosting.remoteds.us;
    
    # Your existing configuration
    root /opt/hosting-api;
    # ... rest of config
}
```

### 3. Obtain SSL Certificates
```bash
# Get certificate for hosting management system
sudo certbot --nginx -d hosting.remoteds.us

# Future commands for cigar/tobacco apps when ready:
# sudo certbot --nginx -d cigars.remoteds.us
# sudo certbot --nginx -d tobacco.remoteds.us
```

**During certificate request, certbot will ask:**
- Email address for renewal notices
- Agree to terms of service
- Share email with EFF (optional)
- Redirect HTTP to HTTPS? (Choose option 2 for redirect)

### 4. Verify Certificate Installation
```bash
# Check certificate status
sudo certbot certificates

# Test SSL configuration
sudo nginx -t

# Test HTTPS access
curl -I https://hosting.remoteds.us
```

### 5. Verify Automatic Renewal
Certbot automatically sets up cron job for renewal. Test it:
```bash
# Test renewal process (dry run)
sudo certbot renew --dry-run

# Check cron job
systemctl list-timers | grep certbot
```

## Certificate Management

### Certificate Location
Certificates are stored in:
```
/etc/letsencrypt/live/hosting.remoteds.us/
├── fullchain.pem    # Certificate + intermediate certificates
├── privkey.pem      # Private key
└── chain.pem        # Intermediate certificates only
```

### Nginx Configuration After Certbot
Certbot automatically updates your Nginx configuration:

```nginx
server {
    server_name hosting.remoteds.us;

    # Redirect HTTP to HTTPS
    listen 80;
    return 301 https://$server_name$request_uri;

    # SSL Configuration (added by certbot)
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/hosting.remoteds.us/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/hosting.remoteds.us/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Your existing configuration
    root /opt/hosting-api;
    # ... rest of config
}
```

## Security Configuration

### SSL Parameters
Certbot installs strong SSL configuration in `/etc/letsencrypt/options-ssl-nginx.conf`:

```nginx
# Strong protocols and ciphers
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
ssl_session_timeout 1d;
ssl_session_cache shared:MozTLS:10m;
```

### Security Headers
Add security headers to your Nginx configuration:

```nginx
# Add to server block in HTTPS section
add_header Strict-Transport-Security "max-age=63072000" always;
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header Referrer-Policy "strict-origin-when-cross-origin";
```

## Monitoring and Maintenance

### Certificate Expiry Monitoring
```bash
# Check certificate expiration
echo | openssl s_client -connect hosting.remoteds.us:443 2>/dev/null | openssl x509 -noout -dates

# Check all certificates
sudo certbot certificates
```

### Manual Renewal (if needed)
```bash
# Force renewal (before 60 days)
sudo certbot renew --force-renewal

# Renew specific certificate
sudo certbot renew --cert-name hosting.remoteds.us
```

### Troubleshooting

#### Common Issues
1. **DNS not propagated**: Ensure domains point to server IP
2. **Port 80 blocked**: Make sure HTTP (port 80) is accessible for validation
3. **Nginx configuration errors**: Test with `sudo nginx -t`

#### Renewal Failures
```bash
# Check renewal logs
sudo journalctl -u certbot -n 50

# Manual renewal with debug output
sudo certbot renew --dry-run --verbose

# Reset certificates if corrupted
sudo certbot delete --cert-name hosting.remoteds.us
sudo certbot --nginx -d hosting.remoteds.us
```

## Future Applications

### Adding Cigar Management System
```bash
# Once cigar app is deployed and DNS configured:
sudo certbot --nginx -d cigars.remoteds.us
```

### Adding Tobacco Management System
```bash
# Once tobacco app is deployed and DNS configured:
sudo certbot --nginx -d tobacco.remoteds.us
```

### Multiple Domains in Single Certificate
```bash
# Alternative: Get one certificate for all domains
sudo certbot --nginx -d hosting.remoteds.us -d cigars.remoteds.us -d tobacco.remoteds.us
```

## Emergency Procedures

### Certificate Revocation
```bash
# Revoke certificate (if private key compromised)
sudo certbot revoke --cert-path /etc/letsencrypt/live/hosting.remoteds.us/fullchain.pem
```

### Nginx Rollback
```bash
# If SSL breaks access, temporary disable SSL
sudo cp /etc/nginx/sites-available/hosting.remoteds.us.backup /etc/nginx/sites-available/hosting.remoteds.us
sudo nginx -t && sudo systemctl reload nginx
```

## ✅ SSL SETUP COMPLETED

### What Was Implemented
1. ✅ **Certbot Installed**: Let's Encrypt certificate management
2. ✅ **SSL Certificate Obtained**: Trusted certificate for hosting.remoteds.us
3. ✅ **Nginx Configuration Updated**: Automatic SSL setup and HTTP→HTTPS redirect
4. ✅ **Auto-renewal Configured**: Cron job for certificate renewal
5. ✅ **Security Hardening**: Strong SSL parameters and security headers
6. ✅ **Monitoring Ready**: Certificate expiration tracking

### Working URLs
- **Hosting Management**: https://hosting.remoteds.us (HTTPS only)
- **HTTP Redirect**: http://hosting.remoteds.us → https://hosting.remoteds.us
- **Future**: https://cigars.remoteds.us, https://tobacco.remoteds.us

### Certificate Details
- **Type**: Let's Encrypt (trusted by all browsers)
- **Validity**: 90 days (auto-renewed)
- **Protocol**: TLSv1.2, TLSv1.3
- **Renewal**: Automatic via certbot cron job

### Browser Compatibility
✅ No browser warnings (trusted certificate)
✅ Green padlock displayed
✅ Compatible with all modern browsers
✅ Mobile friendly

## Integration with Deployment Scripts

### Automated SSL Setup
The SSL setup should be integrated into the deployment scripts:

```python
# In manager.py deployment process
def setup_ssl(domain):
    """Automated SSL setup with certbot"""
    commands = [
        'apt install -y certbot python3-certbot-nginx',
        f'certbot --nginx -d {domain} --non-interactive --agree-tos --email admin@{domain}',
        'certbot renew --dry-run'  # Test renewal
    ]
    
    for cmd in commands:
        conn.sudo(cmd)
```

### SSL Validation in Deployment
```bash
# Part of deployment verification
curl -I https://hosting.remoteds.us
echo | openssl s_client -connect hosting.remoteds.us:443 2>/dev/null | openssl x509 -noout -dates
```

This provides modern, browser-compatible HTTPS with automatic renewal for all applications.

---

## 📖 **Authoritative Documentation**

This document is part of the authoritative documentation set. See **[agents.md](../agents.md)** for:
- Complete documentation hierarchy and reading requirements
- Security protocols and compliance guidelines
- System architecture specifications
- Cross-references to all related documentation

### **Related Documentation**
- **[agents.md](../agents.md)**: AI agent protocols and authoritative documentation links
- **[SECURITY_GUIDE.md](SECURITY_GUIDE.md)**: Complete security protocols
- **[DEPLOYMENT_PRACTICES.md](DEPLOYMENT_PRACTICES.md)**: Security protocols and deployment methods
- **[COMPLETE_DEPLOYMENT_GUIDE.md](COMPLETE_DEPLOYMENT_GUIDE.md)**: Application-specific deployment procedures
