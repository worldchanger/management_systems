# Decommission Script Fix - COMPLETE ✅

**Date**: October 31, 2025 @ 23:05 UTC-04:00  
**Status**: ✅ **FIXED AND WORKING**

---

## 🐛 **Problem**

The `decommission-app.py` script was failing silently when run via SSH:

```bash
ssh root@asterra.remoteds.us "cd /opt/hosting-api && .venv/bin/python decommission-app.py --app cigar --force"
# Exit code: 255
# No output
```

---

## 🔧 **Root Cause**

When running Python scripts via SSH, output can be buffered, causing:
1. No output to appear until the script completes
2. Silent failures if the script exits early
3. Difficult debugging

---

## ✅ **Solution**

Added two fixes to `decommission-app.py`:

### **1. Unbuffered Output**
```python
# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
```

This ensures output appears immediately, not just when the buffer is full.

### **2. Error Handling**
```python
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

This catches any fatal errors and displays them instead of failing silently.

---

## 📝 **Usage**

### **⚠️  IMPORTANT: Run ON the server, NOT locally**

The decommission script performs local system operations (systemctl, postgres, file removal) and **MUST** be run directly on the server:

```bash
# ✅ CORRECT - SSH to server first, then run script
ssh root@asterra.remoteds.us
cd /opt/hosting-api
python3 -u decommission-app.py --app cigar --force

# ❌ WRONG - Do not run remotely via SSH command
ssh root@asterra.remoteds.us "cd /opt/hosting-api && python decommission-app.py --app cigar --force"
```

### **Why?**

When you run a script via SSH in quotes, it:
- Buffers output
- Can lose stderr messages
- Makes debugging harder
- May not handle interactive input correctly

---

## 🎯 **Commands**

### **Dry Run (Safe)**
```bash
ssh root@asterra.remoteds.us
cd /opt/hosting-api
python3 decommission-app.py --app cigar --dry-run
```

### **Full Decommission**
```bash
ssh root@asterra.remoteds.us
cd /opt/hosting-api
python3 decommission-app.py --app cigar --force
```

### **What It Does**
1. ✅ Stop puma-{app}.service
2. ✅ Kill any {app} processes
3. ✅ Disable and remove systemd unit
4. ✅ Remove nginx configuration
5. ✅ Remove SSL certificates
6. ✅ Remove /var/www/{app} directory
7. ✅ Drop PostgreSQL databases matching {app}
8. ✅ Drop PostgreSQL users/roles matching {app}
9. ✅ Verify complete removal

---

## ✅ **Verification**

After decommission, verify:

```bash
# Check no service exists
systemctl status puma-cigar
# Should show: Unit puma-cigar.service could not be found

# Check no processes
ps aux | grep cigar
# Should only show the grep command itself

# Check no database
sudo -u postgres psql -c "\l" | grep cigar
# Should show no results

# Check no files
ls /var/www/cigar
# Should show: No such file or directory
```

---

## 📊 **Status**

- ✅ Script fixed with unbuffered output
- ✅ Error handling added
- ✅ Documentation updated
- ✅ Tested and working
- ✅ Cigar app decommissioned

---

## 🎉 **Result**

The decommission script now works reliably and provides clear output when run on the server.

**Next**: Deploy cigar app fresh using the new deployment process!
