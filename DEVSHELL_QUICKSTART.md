# DevShell.ps1 Quick Start Guide

## 🚀 REAL WORKING EXAMPLE - Copy These Exact Commands

### Step 1: Load DevShell for SeaTrace PUBLIC Work
```powershell
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction
```

**What happens:**
- Script loads and checks environment
- Changes to `C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO`
- Prompt shows: `[🌊 SeaTrace-PUBLIC] PS C:\...\SeaTrace-ODOO>`
- All navigation aliases become available

---

### Step 2: Check Your Current Context
```powershell
project-context
```

**What you'll see:**
```
Active Project: SeaTraceProduction
Project Path: C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO
Context: worldseafoodproducers.com, Commons Charter, PUL licensing
Git: Branch main, Working tree clean
```

---

### Step 3: Switch to PRIVATE Repo (SeaTrace003)
```powershell
cd-seatrace003
```

**What happens:**
- Changes to `C:\Users\Roberto002\Documents\GitHub\SeaTrace003`
- Prompt shows: `[🔒 SeaTrace003-PRIVATE] PS C:\...\SeaTrace003>`
- Context message: "EMR metering, enterprise pricing, investor documentation"

---

### Step 4: Switch Back to PUBLIC Repo
```powershell
cd-seatrace-prod
```

**What happens:**
- Changes to `C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO`
- Prompt shows: `[🌊 SeaTrace-PUBLIC] PS C:\...\SeaTrace-ODOO>`
- Context message: "worldseafoodproducers.com, Commons Charter, PUL licensing"

---

### Step 5: Switch to Sir James Project
```powershell
cd-sirjames
```

**What happens:**
- Changes to Sir James directory
- Prompt shows: `[📚 Sir James] PS C:\...\Sir James>`
- Context message: "Educational content, Netlify deployment, Docker assets"

---

## 📋 Available Commands (After DevShell Loads)

### Navigation
- `cd-seatrace-prod` - Switch to SeaTrace-ODOO (PUBLIC)
- `cd-seatrace003` - Switch to SeaTrace003 (PRIVATE)
- `cd-sirjames` - Switch to Sir James
- `cd-seatrace` - Switch to SeaTrace Development

### Open in VS Code
- `seatrace-prod-code` - Open SeaTrace-ODOO in VS Code
- `seatrace003-code` - Open SeaTrace003 in VS Code
- `sirjames-code` - Open Sir James in VS Code

### Context Info
- `project-context` - Show current project details
- `show-context` - Same as project-context

### System Tools
- `windsurf-status` - Check Windsurf integration
- `windsurf-fix` - Fix Windsurf DLL issues
- `build-assets` - Generate Sir James assets

---

## 🎯 Real Workflow Example

### Scenario: Working on SeaTrace PUBLIC, then switching to PRIVATE

```powershell
# 1. Start in PUBLIC repo
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction

# 2. Check what you're working on
project-context

# 3. Make some changes to public docs
code docs/licensing/COMMONS_CHARTER.md

# 4. Commit public changes
git add docs/licensing/COMMONS_CHARTER.md
git commit -m "docs: update Commons Charter"
git push origin main

# 5. Switch to PRIVATE repo for pricing work
cd-seatrace003

# 6. Verify you're in PRIVATE repo
project-context

# 7. Work on EMR pricing
code src/emr/meter.py

# 8. Commit private changes
git add src/emr/meter.py
git commit -m "feat: update EMR pricing tiers"
git push origin main

# 9. Switch back to PUBLIC
cd-seatrace-prod
```

---

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T DO THIS:
```powershell
# Don't try to run DevShell.ps1 from wrong directory
cd C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO
.\DevShell.ps1  # This won't work - file doesn't exist here
```

### ✅ DO THIS INSTEAD:
```powershell
# Always use full path to DevShell.ps1
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction
```

---

## 🔧 Troubleshooting

### Problem: "cd-seatrace-prod: The term is not recognized"
**Solution:** You haven't loaded DevShell.ps1 yet. Run the full command first.

### Problem: PSReadLine warning appears
**Solution:** This is harmless. The script still works. Copilot fixed this in the latest version.

### Problem: Wrong project context
**Solution:** Run `project-context` to see where you are, then use `cd-*` commands to switch.

---

## 📝 Tell Copilot This

When asking Copilot for help:

**For PUBLIC work:**
```
"I'm working on SeaTrace.worldseafoodproducers.com (PUBLIC repo). 
Help me update the Commons Charter documentation."
```

**For PRIVATE work:**
```
"I'm working on SeaTrace003 (PRIVATE repo).
Help me add a new EMR pricing tier."
```

**For Sir James:**
```
"I'm working on Sir James educational content.
Help me create a new chapter asset."
```

Copilot will see `$env:ACTIVE_PROJECT_CONTEXT` and know which repo to work in.
