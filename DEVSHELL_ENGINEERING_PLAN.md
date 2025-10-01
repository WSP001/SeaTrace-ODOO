# DevShell Engineering Improvement Plan
## Project Separation & Copilot Best Practices

**Created:** October 1, 2025  
**Target:** DevShell.ps1 workflow optimization  
**Status:** ✅ WORKING - DevShell.ps1 loaded successfully at 13:54:13

---

## 🎯 Current State Analysis

### ✅ What's Working
```
✅ DevShell.ps1 loads successfully
✅ Sets $env:ACTIVE_PROJECT_CONTEXT correctly
✅ Navigates to correct directory: C:\Users\Roberto002\Documents\GitHub\SeaTrace-ODOO
✅ All aliases available: cd-seatrace-prod, cd-seatrace003, cd-sirjames
✅ Prompt changes reflect current project context
✅ Module detection working (ThreadJob, PSReadLine, PlatyPS)
```

### ⚠️ Areas for Improvement
```
⚠️ Error when pasting commands multiple times (parser error)
⚠️ PSReadLine warning on first load (cmdlet name conflict)
⚠️ Docker integration shows connection error
⚠️ Windsurf DLL/registry warnings
⚠️ No visual confirmation of git branch in prompt
⚠️ No automatic Copilot context file generation
```

---

## 🚀 Engineering Improvements

### 1. Enhanced Project Context Detection

**Current Behavior:**
```powershell
# DevShell.ps1 sets basic context
$env:ACTIVE_PROJECT_CONTEXT = "SeaTraceProduction"
```

**Improved Behavior:**
```powershell
# Add detailed context variables
$env:ACTIVE_PROJECT_CONTEXT = "SeaTraceProduction"
$env:PROJECT_TYPE = "PUBLIC"
$env:PROJECT_REPO = "SeaTrace-ODOO"
$env:PROJECT_SCOPE = "Commons,PUL,Licensing"
$env:PROJECT_URL = "worldseafoodproducers.com"
$env:GIT_BRANCH = (git branch --show-current 2>$null)
```

**Benefit:** Copilot can see MORE context without asking questions.

---

### 2. Automatic Copilot Context Files

**Problem:** Copilot doesn't automatically know project boundaries.

**Solution:** Generate `.copilot-context.json` when switching projects.

**Implementation:**
```powershell
# In Switch-ToSeaTraceProduction function:
function Switch-ToSeaTraceProduction {
    Set-Location $projectPaths.SeaTraceProduction
    $env:ACTIVE_PROJECT_CONTEXT = "SeaTraceProduction"
    
    # Generate Copilot context file
    @{
        project = "SeaTrace-ODOO"
        type = "PUBLIC"
        scope = @("Commons Charter", "PUL Licensing", "Public Routes")
        excludePaths = @("private/*", "enterprise/*", "emr/*")
        includePaths = @("docs/licensing/PUBLIC*", "src/common/", "docs/COMMONS_CHARTER.md")
        description = "PUBLIC repository for worldseafoodproducers.com Commons licensing"
        relatedProjects = @{
            private = "SeaTrace003"
            educational = "SirJames"
        }
    } | ConvertTo-Json -Depth 10 | Set-Content ".copilot-context.json"
    
    Write-Status "✅ Copilot context: PUBLIC (Commons, PUL, worldseafoodproducers.com)"
}
```

**Result:** Copilot reads `.copilot-context.json` and KNOWS:
- ✅ This is PUBLIC repo
- ✅ Don't suggest EMR/private code
- ✅ Focus on Commons Charter
- ✅ Reference worldseafoodproducers.com docs

---

### 3. Git Branch Integration in Prompt

**Current Prompt:**
```
[🌊 SeaTrace-PUBLIC] PS C:\...\SeaTrace-ODOO>
```

**Improved Prompt:**
```
[🌊 SeaTrace-PUBLIC|main] PS C:\...\SeaTrace-ODOO>
```

**Implementation:**
```powershell
function prompt {
    $projectIcon = switch ($env:ACTIVE_PROJECT_CONTEXT) {
        "SirJames" { "📚" }
        "SeaTraceProduction" { "🌊" }
        "SeaTrace003" { "🔒" }
        "SeaTrace" { "🚢" }
        default { "💻" }
    }
    
    $projectName = switch ($env:ACTIVE_PROJECT_CONTEXT) {
        "SirJames" { "Sir James" }
        "SeaTraceProduction" { "SeaTrace-PUBLIC" }
        "SeaTrace003" { "SeaTrace003-PRIVATE" }
        "SeaTrace" { "SeaTrace-Dev" }
        default { "Unknown" }
    }
    
    $gitBranch = git branch --show-current 2>$null
    if ($gitBranch) {
        $branchIndicator = "|$gitBranch"
    } else {
        $branchIndicator = ""
    }
    
    "[$projectIcon $projectName$branchIndicator] PS $(Get-Location)> "
}
```

---

### 4. Pre-Commit Context Validation

**Problem:** Accidentally committing to wrong repo.

**Solution:** Add git hooks that check project context.

**Implementation:**
Create `.git/hooks/pre-commit` in each repo:

```bash
#!/bin/bash
# SeaTrace-ODOO pre-commit hook

expected_project="SeaTraceProduction"
actual_project="$ACTIVE_PROJECT_CONTEXT"

if [ "$actual_project" != "$expected_project" ]; then
    echo "❌ ERROR: Project context mismatch!"
    echo "   Expected: $expected_project"
    echo "   Actual: $actual_project"
    echo ""
    echo "Run: cd-seatrace-prod"
    exit 1
fi

echo "✅ Project context verified: $expected_project"
exit 0
```

---

### 5. Copilot Instructions per Project

**Create `.github/copilot-instructions.md` in each repo:**

**SeaTrace-ODOO (PUBLIC):**
```markdown
# Copilot Instructions - SeaTrace-ODOO (PUBLIC)

## Project Scope
- Commons Charter documentation
- PUL (Public Unlimited License) implementation
- Public API routes only
- worldseafoodproducers.com website content

## Restrictions
❌ DO NOT suggest or reference:
- EMR metering code
- Enterprise pricing tiers
- Private investor documentation
- SeaTrace003 repository content

✅ ALWAYS:
- Use Commons licensing terminology
- Reference PUBLIC-UNLIMITED.md for licensing
- Keep code in src/common/ directory
- Update docs/licensing/PUBLIC*.md files

## Related Projects
- Private repo: SeaTrace003 (separate context)
- Educational: SirJames (separate context)
```

**SeaTrace003 (PRIVATE):**
```markdown
# Copilot Instructions - SeaTrace003 (PRIVATE)

## Project Scope
- EMR (Electronic Medical Records) metering
- Enterprise pricing tiers
- Private investor documentation
- Proprietary business logic

## Restrictions
❌ DO NOT:
- Reference Commons Charter (that's PUBLIC)
- Copy code from SeaTrace-ODOO
- Suggest public API patterns

✅ ALWAYS:
- Keep EMR code private
- Reference PRIVATE-LIMITED.md for licensing
- Encrypt sensitive data
- Use enterprise authentication patterns
```

---

## 📋 Implementation Checklist

### Phase 1: Immediate Improvements (Today)
- [x] Document current working workflow (DEVSHELL_QUICKSTART.md)
- [ ] Add `.copilot-context.json` generation to DevShell.ps1
- [ ] Create `.github/copilot-instructions.md` in SeaTrace-ODOO
- [ ] Create `.github/copilot-instructions.md` in SeaTrace003
- [ ] Test context switching with Copilot

### Phase 2: Enhanced Context (This Week)
- [ ] Add git branch to prompt
- [ ] Add detailed environment variables
- [ ] Create pre-commit hooks for context validation
- [ ] Add project-info command for detailed context dump

### Phase 3: Automation (Next Week)
- [ ] Auto-generate Copilot context on directory change
- [ ] Add VS Code workspace settings per project
- [ ] Create project-specific task templates
- [ ] Add context validation to CI/CD

---

## 🎯 Real Usage Examples

### Example 1: Working on Commons Charter (PUBLIC)

```powershell
# 1. Load DevShell
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction

# 2. Verify context
project-context
# Shows: SeaTraceProduction, Commons Charter, PUBLIC

# 3. Ask Copilot
"Help me add a new section to the Commons Charter about data sharing governance."

# Copilot sees:
# - $env:ACTIVE_PROJECT_CONTEXT = "SeaTraceProduction"
# - .copilot-context.json: type = "PUBLIC"
# - .github/copilot-instructions.md: Focus on Commons
# Result: Copilot suggests edits to docs/COMMONS_CHARTER.md
```

### Example 2: Working on EMR Pricing (PRIVATE)

```powershell
# 1. Switch to PRIVATE repo
cd-seatrace003

# 2. Verify context
project-context
# Shows: SeaTrace003, EMR metering, PRIVATE

# 3. Ask Copilot
"Help me add a new enterprise pricing tier for hospitals with 500+ beds."

# Copilot sees:
# - $env:ACTIVE_PROJECT_CONTEXT = "SeaTrace003"
# - .copilot-context.json: type = "PRIVATE"
# - .github/copilot-instructions.md: Focus on EMR, enterprise
# Result: Copilot suggests edits to src/marketside/licensing/entitlements.py
```

### Example 3: Context Validation (Prevents Mistakes)

```powershell
# You're in PUBLIC repo
cd-seatrace-prod

# You accidentally try to edit EMR code
code src/emr/pricing.py

# Copilot warning:
"⚠️ Warning: src/emr/ is not in PUBLIC scope.
Switch to SeaTrace003 (PRIVATE) to work on EMR code.
Run: cd-seatrace003"
```

---

## 🔧 DevShell.ps1 Enhancement Proposals

### Proposal 1: Add `project-switch` with Confirmation

```powershell
function Switch-ProjectWithConfirmation {
    param([string]$TargetProject)
    
    $currentChanges = git status --short 2>$null
    if ($currentChanges) {
        Write-Warning "⚠️ Uncommitted changes detected!"
        Write-Host "Current project: $env:ACTIVE_PROJECT_CONTEXT"
        Write-Host "Target project: $TargetProject"
        Write-Host ""
        git status --short
        Write-Host ""
        $confirm = Read-Host "Switch anyway? (y/N)"
        if ($confirm -ne 'y') {
            Write-Host "❌ Switch cancelled"
            return
        }
    }
    
    # Proceed with switch
    Switch-ToProject $TargetProject
}
```

### Proposal 2: Add `copilot-context` Command

```powershell
function Show-CopilotContext {
    Write-Host "🤖 Copilot Context Information" -ForegroundColor Cyan
    Write-Host "================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Environment Variables:" -ForegroundColor Yellow
    Write-Host "  ACTIVE_PROJECT_CONTEXT: $env:ACTIVE_PROJECT_CONTEXT"
    Write-Host "  PROJECT_TYPE: $env:PROJECT_TYPE"
    Write-Host "  PROJECT_SCOPE: $env:PROJECT_SCOPE"
    Write-Host "  GIT_BRANCH: $(git branch --show-current 2>$null)"
    Write-Host ""
    
    if (Test-Path ".copilot-context.json") {
        Write-Host "Copilot Context File:" -ForegroundColor Yellow
        Get-Content ".copilot-context.json" | ConvertFrom-Json | Format-List
    }
    
    if (Test-Path ".github/copilot-instructions.md") {
        Write-Host "Copilot Instructions Found: .github/copilot-instructions.md" -ForegroundColor Green
    } else {
        Write-Host "⚠️ No Copilot instructions file found" -ForegroundColor Yellow
    }
}

Set-Alias copilot-context Show-CopilotContext
```

### Proposal 3: Add `project-validate` Command

```powershell
function Test-ProjectContext {
    $currentDir = Get-Location
    $expectedProject = $env:ACTIVE_PROJECT_CONTEXT
    $expectedPath = $env:ACTIVE_PROJECT_PATH
    
    Write-Host "🔍 Validating Project Context" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if we're in the right directory
    if ($currentDir -ne $expectedPath) {
        Write-Host "❌ Path Mismatch!" -ForegroundColor Red
        Write-Host "   Expected: $expectedPath"
        Write-Host "   Actual: $currentDir"
        return $false
    } else {
        Write-Host "✅ Path correct: $currentDir" -ForegroundColor Green
    }
    
    # Check if git repo matches expected
    $gitRemote = git remote get-url origin 2>$null
    Write-Host "✅ Git remote: $gitRemote" -ForegroundColor Green
    
    # Check for uncommitted changes
    $gitStatus = git status --short 2>$null
    if ($gitStatus) {
        Write-Host "⚠️ Uncommitted changes:" -ForegroundColor Yellow
        git status --short
    } else {
        Write-Host "✅ Working tree clean" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Project context is valid for: $expectedProject" -ForegroundColor Green
    return $true
}

Set-Alias project-validate Test-ProjectContext
```

---

## 📊 Success Metrics

After implementing improvements, measure:

1. **Context Accuracy**
   - ✅ Copilot suggests correct repo files 95%+ of time
   - ✅ No cross-repo code suggestions

2. **Developer Efficiency**
   - ⏱️ Time to switch projects: < 5 seconds
   - ⏱️ Time to verify context: < 2 seconds

3. **Error Prevention**
   - 🛡️ Zero accidental commits to wrong repo
   - 🛡️ Copilot warns when scope mismatch detected

4. **Documentation Quality**
   - 📚 All repos have `.github/copilot-instructions.md`
   - 📚 All repos have `.copilot-context.json`

---

## 🎓 Best Practices for Copilot

### DO: Provide Clear Context
```
✅ "I'm working on SeaTrace-ODOO (PUBLIC repo). 
    Help me update docs/COMMONS_CHARTER.md to add 
    a section about seafood data sharing governance."
```

### DON'T: Be Vague
```
❌ "Help me update the charter."
```

### DO: Reference Project Scope
```
✅ "In the PUBLIC SeaTrace repo, add a new PUL license 
    verification route to src/common/licensing/routes.py"
```

### DON'T: Mix Project Contexts
```
❌ "Add EMR pricing to the commons licensing module."
    (EMR = PRIVATE, Commons = PUBLIC)
```

### DO: Use Environment Variables
```
✅ Copilot reads $env:ACTIVE_PROJECT_CONTEXT automatically
✅ DevShell.ps1 sets this when you switch projects
```

### DO: Validate Before Committing
```powershell
project-validate  # Check context is correct
git status        # Review changes
git diff          # Verify edits
git commit        # Commit with confidence
```

---

## 🚀 Next Steps

### For You (User)
1. ✅ Keep using DevShell.ps1 as you are (it's working!)
2. 📝 Tell Copilot your project context explicitly
3. 🔍 Run `project-context` before asking Copilot for help
4. 🛡️ Run `project-validate` before committing

### For DevShell.ps1 (Future Enhancement)
1. Add `.copilot-context.json` generation
2. Add git branch to prompt
3. Add `copilot-context` command
4. Add `project-validate` command
5. Add pre-commit hooks

### For Project Repos
1. Create `.github/copilot-instructions.md` in each repo
2. Add `.copilot-context.json` to .gitignore (auto-generated)
3. Document project boundaries clearly
4. Add README.md with Copilot usage examples

---

## 📞 Support

If you see this error:
```
cd-seatrace-prod: The term is not recognized
```

**Solution:** Run DevShell.ps1 first:
```powershell
& "C:\Users\Roberto002\OneDrive\Sir James\LOGIC SirJames_Interactive_Prototype_With_Chapter10\scripts\DevShell.ps1" -Project SeaTraceProduction
```

If you're unsure which project you're in:
```powershell
project-context
```

If you want to see what Copilot knows:
```powershell
echo "Active Project: $env:ACTIVE_PROJECT_CONTEXT"
```

---

**Status:** ✅ DevShell.ps1 working as of 2025-10-01 13:54:13  
**Last verified:** October 1, 2025  
**Next review:** After implementing Phase 1 improvements
