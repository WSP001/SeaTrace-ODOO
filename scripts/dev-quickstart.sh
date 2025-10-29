#!/usr/bin/env bash
# dev-quickstart.sh - SeaTrace WSL Development Environment Bootstrap
# Author: SeaTrace Programming Team
# Last Updated: 2025-10-28
# 
# Purpose: Safely bootstrap WSL2 (Ubuntu) development environment for SeaTrace
# Usage: bash dev-quickstart.sh
#
# What this script does:
# 1. Installs essential build tools (gcc, make, curl, git, python3, jq)
# 2. Installs nvm (Node Version Manager) + Node LTS
# 3. Configures safe npm global prefix (no sudo required)
# 4. Installs Newman (Postman CLI) for CI testing
# 5. Optionally installs @google/gemini-cli
# 6. Creates Python venv for SeaTrace repos
# 7. Configures ssh-agent for Git operations
# 8. Provides post-install instructions

set -euo pipefail

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Workspace paths
WORKSPACE_ROOT="/mnt/c/Users/Roberto002/Documents/GitHub"
SEATRACE_ODOO="$WORKSPACE_ROOT/SeaTrace-ODOO"
SEATRACE_002="$WORKSPACE_ROOT/SeaTrace002"
SEATRACE_003="$WORKSPACE_ROOT/SeaTrace003"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
print_header() {
  echo -e "\n${BLUE}===== $1 =====${NC}\n"
}

print_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
  echo -e "${RED}❌ $1${NC}"
}

confirm_proceed() {
  local prompt="${1:-Proceed?}"
  local default="${2:-Y}"
  
  read -p "$(echo -e ${YELLOW}${prompt} [${default}/n]: ${NC})" response
  response=${response:-$default}
  
  if [[ ! "$response" =~ ^[Yy] ]]; then
    print_warning "Aborted by user."
    exit 0
  fi
}

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================
print_header "SeaTrace WSL Dev Environment Bootstrap"

echo "This script will:"
echo "  • Update system packages (requires sudo)"
echo "  • Install nvm + Node LTS"
echo "  • Install Newman (Postman CLI)"
echo "  • Configure safe npm global prefix"
echo "  • Create Python venvs for SeaTrace repos"
echo "  • Configure ssh-agent"
echo ""
echo "Workspaces detected:"
[ -d "$SEATRACE_ODOO" ] && echo "  ✅ SeaTrace-ODOO (public docs)"
[ -d "$SEATRACE_002" ] && echo "  ✅ SeaTrace002 (private legacy)"
[ -d "$SEATRACE_003" ] && echo "  ✅ SeaTrace003 (private production)"
echo ""

confirm_proceed "Continue with installation?"

# ============================================================================
# SYSTEM PACKAGE INSTALLATION
# ============================================================================
print_header "Updating System Packages"

sudo apt update
sudo apt upgrade -y
sudo apt install -y \
  build-essential \
  curl \
  wget \
  git \
  unzip \
  jq \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  libssl-dev \
  ca-certificates

print_success "System packages installed"

# ============================================================================
# NVM (Node Version Manager) INSTALLATION
# ============================================================================
print_header "Installing NVM (Node Version Manager)"

if [ -d "$HOME/.nvm" ]; then
  print_warning "nvm already installed at $HOME/.nvm"
else
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash
  
  # Load nvm for current session
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
  
  print_success "nvm installed"
fi

# Load nvm if not already loaded
if ! command -v nvm >/dev/null 2>&1; then
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
fi

# ============================================================================
# NODE.JS LTS INSTALLATION
# ============================================================================
print_header "Installing Node.js LTS"

nvm install --lts
nvm use --lts

NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)

print_success "Node.js $NODE_VERSION installed"
print_success "npm $NPM_VERSION installed"

# ============================================================================
# SAFE NPM GLOBAL PREFIX
# ============================================================================
print_header "Configuring Safe npm Global Prefix"

mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"
export PATH="$HOME/.npm-global/bin:$PATH"

# Add to .bashrc if not already present
if ! grep -q "NPM_GLOBAL_PREFIX" "$HOME/.bashrc" 2>/dev/null; then
  echo "" >> "$HOME/.bashrc"
  echo "# Safe npm global prefix (added by dev-quickstart.sh)" >> "$HOME/.bashrc"
  echo 'export NPM_GLOBAL_PREFIX="$HOME/.npm-global"' >> "$HOME/.bashrc"
  echo 'export PATH="$NPM_GLOBAL_PREFIX/bin:$PATH"' >> "$HOME/.bashrc"
  print_success "npm global prefix configured in .bashrc"
fi

print_success "npm global prefix: $HOME/.npm-global"

# ============================================================================
# NEWMAN (Postman CLI) INSTALLATION
# ============================================================================
print_header "Installing Newman (Postman CLI)"

npm install -g newman

print_success "Newman installed: $(newman --version)"

# ============================================================================
# OPTIONAL: GEMINI CLI INSTALLATION
# ============================================================================
print_header "Optional: Gemini CLI"

echo "The @google/gemini-cli provides LLM integration for prototyping."
echo "You can install it globally or use 'npx @google/gemini-cli' instead."
echo ""

confirm_proceed "Install @google/gemini-cli globally?" "n"

if [[ "$response" =~ ^[Yy] ]]; then
  npm install -g @google/gemini-cli || print_warning "gemini-cli install failed (try npx instead)"
  print_success "gemini-cli installed (if successful)"
else
  print_success "Skipped gemini-cli (use npx @google/gemini-cli when needed)"
fi

# ============================================================================
# PYTHON VIRTUAL ENVIRONMENTS
# ============================================================================
print_header "Creating Python Virtual Environments"

create_python_venv() {
  local repo_path="$1"
  local repo_name=$(basename "$repo_path")
  
  if [ ! -d "$repo_path" ]; then
    print_warning "Repo not found: $repo_name (skipping)"
    return
  fi
  
  cd "$repo_path"
  
  if [ -d ".venv" ]; then
    print_warning "$repo_name: .venv already exists (skipping)"
    return
  fi
  
  echo "Creating venv for $repo_name..."
  python3 -m venv .venv
  . .venv/bin/activate
  pip install --upgrade pip
  
  # Install requirements if present
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "$repo_name: Installed requirements.txt"
  elif [ -f "pyproject.toml" ]; then
    pip install -e .
    print_success "$repo_name: Installed from pyproject.toml"
  else
    # Install common dev packages for SeaTrace
    pip install pytest pytest-asyncio black flake8 mypy
    print_success "$repo_name: Installed common dev packages"
  fi
  
  deactivate
}

# Create venvs for all detected repos
create_python_venv "$SEATRACE_ODOO"
create_python_venv "$SEATRACE_002"
create_python_venv "$SEATRACE_003"

# ============================================================================
# SSH-AGENT CONFIGURATION
# ============================================================================
print_header "Configuring SSH Agent"

# Check for SSH keys
SSH_KEY_WSL="$HOME/.ssh/id_ed25519_work"
SSH_KEY_WIN="/mnt/c/Users/Roberto002/.ssh/id_ed25519_work"

if [ -f "$SSH_KEY_WSL" ]; then
  print_success "Found SSH key: $SSH_KEY_WSL"
  eval "$(ssh-agent -s)" >/dev/null 2>&1
  ssh-add "$SSH_KEY_WSL" 2>/dev/null && print_success "SSH key added to agent"
elif [ -f "$SSH_KEY_WIN" ]; then
  print_success "Found SSH key (Windows): $SSH_KEY_WIN"
  eval "$(ssh-agent -s)" >/dev/null 2>&1
  ssh-add "$SSH_KEY_WIN" 2>/dev/null && print_success "SSH key added to agent"
else
  print_warning "No SSH key found. Generate with: ssh-keygen -t ed25519 -C 'roberto@seatrace'"
fi

# ============================================================================
# GITLEAKS INSTALLATION (Optional Secret Scanner)
# ============================================================================
print_header "Optional: Gitleaks (Secret Scanner)"

echo "Gitleaks scans git repos for accidentally committed secrets."
confirm_proceed "Install gitleaks?" "n"

if [[ "$response" =~ ^[Yy] ]]; then
  if command -v go >/dev/null 2>&1; then
    go install github.com/zricethezav/gitleaks/v8@latest
    print_success "Gitleaks installed via go"
  else
    print_warning "Go not installed. Install gitleaks manually or skip."
  fi
else
  print_success "Skipped gitleaks"
fi

# ============================================================================
# BASHRC INTEGRATION
# ============================================================================
print_header "Integrating SeaTrace .bashrc"

BASHRC_TEMPLATE="$SEATRACE_ODOO/scripts/bashrc_roberto002"

if [ -f "$BASHRC_TEMPLATE" ]; then
  echo ""
  echo "A SeaTrace-optimized .bashrc template exists at:"
  echo "  $BASHRC_TEMPLATE"
  echo ""
  echo "It includes:"
  echo "  • Four Pillars navigation helpers (seaside, deckside, dockside, marketside)"
  echo "  • Terminal divider() function for readable output"
  echo "  • run_in() safety wrapper for directory-specific commands"
  echo "  • Git aliases and custom prompt"
  echo ""
  confirm_proceed "Append SeaTrace .bashrc to your ~/.bashrc?" "Y"
  
  if [[ "$response" =~ ^[Yy] ]]; then
    echo "" >> "$HOME/.bashrc"
    echo "# ============================================================================" >> "$HOME/.bashrc"
    echo "# SEATRACE DEVELOPMENT ENVIRONMENT (added by dev-quickstart.sh)" >> "$HOME/.bashrc"
    echo "# ============================================================================" >> "$HOME/.bashrc"
    cat "$BASHRC_TEMPLATE" >> "$HOME/.bashrc"
    print_success "SeaTrace .bashrc appended to ~/.bashrc"
  else
    print_warning "Skipped .bashrc integration (you can manually source it later)"
  fi
else
  print_warning "SeaTrace .bashrc template not found (expected at $BASHRC_TEMPLATE)"
fi

# ============================================================================
# POST-INSTALL INSTRUCTIONS
# ============================================================================
print_header "Bootstrap Complete! 🎉"

echo ""
echo -e "${GREEN}✅ Environment successfully configured${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Reload your shell:"
echo "   ${BLUE}exec bash${NC}"
echo "   ${BLUE}# or${NC}"
echo "   ${BLUE}source ~/.bashrc${NC}"
echo ""
echo "2️⃣  Verify installations:"
echo "   ${BLUE}node --version${NC}"
echo "   ${BLUE}npm --version${NC}"
echo "   ${BLUE}newman --version${NC}"
echo "   ${BLUE}python3 --version${NC}"
echo ""
echo "3️⃣  Navigate to SeaTrace workspace:"
echo "   ${BLUE}seaodoo${NC}  # or cd $SEATRACE_ODOO"
echo ""
echo "4️⃣  Test Four Pillars helpers (if SeaTrace003 exists):"
echo "   ${BLUE}seaside echo 'Hello from SeaSide'${NC}"
echo "   ${BLUE}deckside echo 'Hello from DeckSide'${NC}"
echo ""
echo "5️⃣  Run SeaTrace startup script:"
echo "   ${BLUE}cd $SEATRACE_003 && ./scripts/start_all.sh${NC}"
echo ""
echo "6️⃣  Run Postman collection (if newman + collection exist):"
echo "   ${BLUE}newman run postman/collection.json -e postman/environment.json${NC}"
echo ""
echo "7️⃣  Activate Python venv (if needed):"
echo "   ${BLUE}cd $SEATRACE_ODOO && source .venv/bin/activate${NC}"
echo ""
echo -e "${YELLOW}⚠️  OpenAI API Key:${NC}"
echo "   When ready to test embeddings, add to ~/.config/seatrace/secrets.env:"
echo "   ${BLUE}export OPENAI_API_KEY='sk-...'${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🌊${NC}"
echo ""
