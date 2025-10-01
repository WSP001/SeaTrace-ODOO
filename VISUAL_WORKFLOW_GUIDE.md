# 🎯 Visual Workflow Guide - DevShell Project Separation

**Date:** October 1, 2025  
**Status:** ✅ VERIFIED WORKING

---

## 🌊 THE BIG PICTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR DEVELOPMENT SETUP                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  DevShell.ps1 (Master Control)                               │
│  Location: C:\Users\Roberto002\OneDrive\Sir James\...        │
│                                                               │
│  When you run:                                               │
│  & "...\DevShell.ps1" -Project SeaTraceProduction            │
│                                                               │
│  It sets up:                                                 │
│  • $env:ACTIVE_PROJECT_CONTEXT = "SeaTraceProduction"        │
│  • Changes to correct directory                              │
│  • Loads aliases (cd-seatrace-prod, cd-seatrace003, etc.)    │
│  • Updates prompt with project indicator                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────┴─────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────┐                     ┌──────────────────────┐
│  PUBLIC PROJECT  │                     │   PRIVATE PROJECT    │
├──────────────────┤                     ├──────────────────────┤
│ SeaTrace-ODOO    │                     │   SeaTrace003        │
│ [🌊 PUBLIC]      │                     │   [🔒 PRIVATE]       │
│                  │                     │                      │
│ Contains:        │                     │ Contains:            │
│ • Commons Charter│                     │ • EMR metering       │
│ • PUL licensing  │                     │ • Enterprise pricing │
│ • Public API     │                     │ • Investor docs      │
│ • worldseafood.. │                     │ • Trade secrets      │
│                  │                     │                      │
│ Directory:       │                     │ Directory:           │
│ C:\Users\        │                     │ C:\Users\            │
│ Roberto002\      │                     │ Roberto002\          │
│ Documents\       │                     │ Documents\           │
│ GitHub\          │                     │ GitHub\              │
│ SeaTrace-ODOO    │                     │ SeaTrace003          │
│                  │                     │                      │
│ Switch with:     │                     │ Switch with:         │
│ cd-seatrace-prod │                     │ cd-seatrace003       │
└──────────────────┘                     └──────────────────────┘
```

---

## 🔄 WORKFLOW: Switching Between Projects

```
┌──────────────────────────────────────────────────────────────┐
│ START: You're in PowerShell                                   │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Load DevShell.ps1                                     │
│ Command: & "C:\Users\Roberto002\OneDrive\Sir James\          │
│           LOGIC SirJames_Interactive_Prototype_With_Chapter10\│
│           scripts\DevShell.ps1" -Project SeaTraceProduction   │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ RESULT: Environment Loaded                                    │
│ • Working in: C:\...\SeaTrace-ODOO                            │
│ • Context: SeaTraceProduction                                 │
│ • Prompt: [🌊 SeaTrace-PUBLIC] PS C:\...\SeaTrace-ODOO>      │
│ • Aliases available: cd-seatrace-prod, cd-seatrace003, etc.   │
└──────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
  ┌────────────┐  ┌────────────┐  ┌────────────┐
  │  PUBLIC    │  │  PRIVATE   │  │  SIR JAMES │
  │  WORK      │  │  WORK      │  │  WORK      │
  └────────────┘  └────────────┘  └────────────┘
         │               │               │
         ▼               ▼               ▼
  cd-seatrace-prod  cd-seatrace003  cd-sirjames
         │               │               │
         ▼               ▼               ▼
  Commons Charter   EMR Pricing    Educational
  PUL Licensing     Enterprise      Content
  Public API        Investors       Assets
```

---

## 📋 DECISION TREE: Which Repo Should I Use?

```
┌─────────────────────────────────────────────────────────────┐
│ What do you want to work on?                                 │
└─────────────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌─────────┐     ┌─────────┐    ┌──────────┐
   │ Commons │     │   EMR   │    │   Sir    │
   │ Charter?│     │ Pricing?│    │  James?  │
   └─────────┘     └─────────┘    └──────────┘
         │               │               │
         │YES            │YES            │YES
         ▼               ▼               ▼
   ┌─────────┐     ┌─────────┐    ┌──────────┐
   │ PUBLIC  │     │ PRIVATE │    │EDUCATION │
   │  REPO   │     │  REPO   │    │   REPO   │
   └─────────┘     └─────────┘    └──────────┘
         │               │               │
         ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────┐
│SeaTrace-ODOO │  │ SeaTrace003  │  │ SirJames │
├──────────────┤  ├──────────────┤  ├──────────┤
│cd-seatrace-  │  │cd-seatrace003│  │cd-sir-   │
│     prod     │  │              │  │  james   │
└──────────────┘  └──────────────┘  └──────────┘

MORE EXAMPLES:

PUL licensing? ────────────────────────► PUBLIC (SeaTrace-ODOO)
Public API routes? ────────────────────► PUBLIC (SeaTrace-ODOO)
worldseafoodproducers.com? ────────────► PUBLIC (SeaTrace-ODOO)
Marketing for Commons? ────────────────► PUBLIC (SeaTrace-ODOO)

EMR metering? ─────────────────────────► PRIVATE (SeaTrace003)
Enterprise subscriptions? ─────────────► PRIVATE (SeaTrace003)
Investor documentation? ───────────────► PRIVATE (SeaTrace003)
Proprietary business logic? ───────────► PRIVATE (SeaTrace003)

Educational adventure? ────────────────► SIR JAMES
Docker asset generation? ──────────────► SIR JAMES
Netlify deployment? ───────────────────► SIR JAMES
```

---

## 🎯 WORKFLOW: Asking Copilot for Help

```
┌──────────────────────────────────────────────────────────────┐
│ YOU: Want to work on something                                │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 1: Verify Context                                        │
│ Command: project-context                                      │
│ Output: Active Project: SeaTraceProduction                    │
│         Context: worldseafoodproducers.com, Commons, PUL      │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 2: Switch Project (if needed)                            │
│ • If working on PUBLIC: cd-seatrace-prod                      │
│ • If working on PRIVATE: cd-seatrace003                       │
│ • If working on Sir James: cd-sirjames                        │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ STEP 3: Tell Copilot Your Context                             │
│ ✅ GOOD: "I'm working on SeaTrace-ODOO (PUBLIC repo).        │
│           Help me update docs/COMMONS_CHARTER.md"            │
│                                                               │
│ ❌ BAD:  "Update the charter"                                │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ COPILOT: Reads Context                                        │
│ • $env:ACTIVE_PROJECT_CONTEXT = "SeaTraceProduction"         │
│ • .github/copilot-instructions.md (scope: PUBLIC)             │
│ • Your explicit statement: "SeaTrace-ODOO (PUBLIC repo)"      │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ COPILOT: Makes Suggestions                                    │
│ ✅ Suggests: Changes to docs/COMMONS_CHARTER.md              │
│ ✅ References: PUBLIC-UNLIMITED.md, Commons principles        │
│ ❌ Won't suggest: EMR code (that's PRIVATE repo)             │
│ ❌ Won't suggest: Enterprise pricing (that's PRIVATE repo)   │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ YOU: Review & Commit                                          │
│ • git diff (review changes)                                   │
│ • git add . (stage changes)                                   │
│ • git commit -m "description" (commit)                        │
│ • git push origin main (push)                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚨 ERROR PREVENTION FLOWCHART

```
┌──────────────────────────────────────────────────────────────┐
│ Before Asking Copilot                                         │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
                ┌────────────────┐
                │  Run:          │
                │  project-      │
                │  context       │
                └────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌─────────┐     ┌─────────┐    ┌──────────┐
   │SeaTrace │     │SeaTrace │    │ SirJames │
   │  -ODOO  │     │   003   │    │          │
   └─────────┘     └─────────┘    └──────────┘
         │               │               │
         ▼               ▼               ▼
   ┌─────────┐     ┌─────────┐    ┌──────────┐
   │ PUBLIC  │     │ PRIVATE │    │EDUCATION │
   │  REPO   │     │  REPO   │    │   REPO   │
   └─────────┘     └─────────┘    └──────────┘
         │               │               │
         ▼               ▼               ▼
   ┌─────────────────────────────────────────┐
   │ Is this the RIGHT repo for your task?   │
   └─────────────────────────────────────────┘
         │               │               │
     ┌───┴───┐       ┌───┴───┐       ┌───┴───┐
     │  YES  │       │  YES  │       │  YES  │
     └───┬───┘       └───┬───┘       └───┬───┘
         │               │               │
         ▼               ▼               ▼
   ┌─────────────────────────────────────────┐
   │ Ask Copilot with EXPLICIT context       │
   │ "I'm working on [REPO NAME]..."         │
   └─────────────────────────────────────────┘
         │               │               │
     ┌───┴───┐       ┌───┴───┐       ┌───┴───┐
     │  NO?  │       │  NO?  │       │  NO?  │
     └───┬───┘       └───┬───┘       └───┬───┘
         │               │               │
         ▼               ▼               ▼
   ┌─────────────────────────────────────────┐
   │ Switch repos first!                     │
   │ cd-seatrace-prod / cd-seatrace003 /     │
   │ cd-sirjames                             │
   └─────────────────────────────────────────┘
```

---

## 📊 CONTEXT INDICATORS REFERENCE

### Terminal Prompt Indicators
```
[🌊 SeaTrace-PUBLIC]       ← You're in PUBLIC repo (SeaTrace-ODOO)
[🔒 SeaTrace003-PRIVATE]   ← You're in PRIVATE repo (SeaTrace003)
[📚 Sir James]             ← You're in Educational repo (SirJames)
[🚢 SeaTrace-Dev]          ← You're in Development environment
```

### Environment Variables
```powershell
$env:ACTIVE_PROJECT_CONTEXT
├─ "SeaTraceProduction" ─► PUBLIC repo (SeaTrace-ODOO)
├─ "SeaTrace003"        ─► PRIVATE repo (SeaTrace003)
├─ "SirJames"           ─► Educational repo (SirJames)
└─ "SeaTrace"           ─► Development environment
```

### Directory Paths
```
C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO  ─► PUBLIC
C:\Users\Roberto002\Documents\GitHub\SeaTrace003    ─► PRIVATE
C:\Users\Roberto002\OneDrive\Sir James\...          ─► EDUCATION
```

---

## 🎯 QUICK DECISION MATRIX

| Task | Repo | Command | Context |
|------|------|---------|---------|
| Update Commons Charter | PUBLIC | `cd-seatrace-prod` | worldseafoodproducers.com |
| Add PUL license route | PUBLIC | `cd-seatrace-prod` | Commons, PUL |
| Generate public scope | PUBLIC | `cd-seatrace-prod` | Public API |
| Update EMR pricing | PRIVATE | `cd-seatrace003` | Enterprise, EMR |
| Add investor docs | PRIVATE | `cd-seatrace003` | Business, Private |
| Work on adventure | EDUCATION | `cd-sirjames` | Educational content |

---

## 🔄 DAILY WORKFLOW DIAGRAM

```
┌───────────────────────────────────────────────────────────┐
│                      START OF DAY                          │
└───────────────────────────────────────────────────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │ Open PowerShell               │
           └───────────────────────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │ Load DevShell.ps1             │
           │ & "...\DevShell.ps1"          │
           │   -Project SeaTraceProduction │
           └───────────────────────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │ Verify: project-context       │
           └───────────────────────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │ Check: git status             │
           └───────────────────────────────┘
                           │
           ┌───────────────┴───────────────┐
           │                               │
           ▼                               ▼
    ┌────────────┐                  ┌────────────┐
    │   PUBLIC   │                  │  PRIVATE   │
    │    WORK    │                  │    WORK    │
    └────────────┘                  └────────────┘
           │                               │
           ▼                               ▼
    cd-seatrace-prod              cd-seatrace003
           │                               │
           ▼                               ▼
    Tell Copilot:                 Tell Copilot:
    "SeaTrace-ODOO                "SeaTrace003
     PUBLIC repo"                  PRIVATE repo"
           │                               │
           ▼                               ▼
    Work on:                      Work on:
    • Commons Charter             • EMR pricing
    • PUL licensing               • Enterprise tiers
    • Public API                  • Investor docs
           │                               │
           ▼                               ▼
    ┌────────────┐                  ┌────────────┐
    │ git diff   │                  │ git diff   │
    │ git add .  │                  │ git add .  │
    │ git commit │                  │ git commit │
    │ git push   │                  │ git push   │
    └────────────┘                  └────────────┘
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
           ┌───────────────────────────────┐
           │        END OF DAY              │
           │   Both repos updated!          │
           └───────────────────────────────┘
```

---

## 📝 COPILOT INTERACTION EXAMPLE

```
┌────────────────────────────────────────────────────────────┐
│ SCENARIO: You want to add data governance section          │
│           to Commons Charter                               │
└────────────────────────────────────────────────────────────┘

STEP 1: Verify Context
┌────────────────────────────────────────────────────────────┐
│ PS C:\...\SeaTrace-ODOO> project-context                   │
│                                                            │
│ Active Project: SeaTraceProduction                         │
│ Project Path: C:\Users\Roberto002\Documents\GitHub\        │
│               SeaTrace-ODOO                                │
│ Context: worldseafoodproducers.com, Commons Charter, PUL   │
│ Git: Branch main, Working tree clean                       │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼ Context is correct!
                           
STEP 2: Ask Copilot
┌────────────────────────────────────────────────────────────┐
│ YOU SAY:                                                   │
│ "I'm working on SeaTrace-ODOO (PUBLIC repo).               │
│  Help me add a new section to docs/COMMONS_CHARTER.md      │
│  about seafood data sharing governance.                    │
│  The section should cover:                                 │
│  - Data ownership principles                               │
│  - Sharing protocols                                       │
│  - Privacy considerations"                                 │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
STEP 3: Copilot Analyzes Context
┌────────────────────────────────────────────────────────────┐
│ COPILOT SEES:                                              │
│ ✅ $env:ACTIVE_PROJECT_CONTEXT = "SeaTraceProduction"     │
│ ✅ .github/copilot-instructions.md says: PUBLIC scope      │
│ ✅ You said explicitly: "SeaTrace-ODOO (PUBLIC repo)"      │
│ ✅ File exists: docs/COMMONS_CHARTER.md                    │
│ ✅ This is appropriate for PUBLIC repo                     │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼
STEP 4: Copilot Suggests
┌────────────────────────────────────────────────────────────┐
│ COPILOT SUGGESTS:                                          │
│ "I'll add a new section 'Data Governance' to               │
│  docs/COMMONS_CHARTER.md covering:                         │
│  - Data ownership under Commons principles                 │
│  - Transparent sharing protocols                           │
│  - Privacy-preserving practices                            │
│                                                            │
│  [Shows code diff with new section]"                       │
│                                                            │
│ ❌ DOES NOT suggest:                                       │
│    - EMR tracking code (PRIVATE repo)                      │
│    - Enterprise pricing (PRIVATE repo)                     │
│    - Sir James content (different project)                 │
└────────────────────────────────────────────────────────────┘
                           │
                           ▼ You approve!
                           
STEP 5: Review & Commit
┌────────────────────────────────────────────────────────────┐
│ PS C:\...\SeaTrace-ODOO> git diff                          │
│ [Shows changes to docs/COMMONS_CHARTER.md]                 │
│                                                            │
│ PS C:\...\SeaTrace-ODOO> git add docs/COMMONS_CHARTER.md   │
│ PS C:\...\SeaTrace-ODOO> git commit -m "docs: add data     │
│   governance section to Commons Charter"                   │
│ PS C:\...\SeaTrace-ODOO> git push origin main              │
│ [✅ Changes pushed to PUBLIC repo]                         │
└────────────────────────────────────────────────────────────┘
```

---

**Your visual workflow guide is complete! 🎯**

Use this diagram when:
- 🤔 Unsure which repo to use
- 🔄 Switching between projects
- 🤖 Asking Copilot for help
- ✅ Verifying context before committing

**Remember:** Context is EVERYTHING!  
Always verify with `project-context` before asking Copilot. 🌊
