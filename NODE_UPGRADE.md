# Node.js 20 Upgrade Guide

## Overview

The frontend tests and tooling require **Node.js 20 or later** due to dependencies on modern packages:

- `vitest@4.x` requires Node 20+
- `jsdom@27.x` requires Node 20+
- `whatwg-url@15.x` requires Node 20+
- `happy-dom@20.x` requires Node 20+

## Current Status

✅ **Configuration Updated** - All configs now specify Node 20:

- `.nvmrc` → Node 20
- `frontend/.nvmrc` → Node 20
- `frontend/package.json` → `engines.node: ">=20.0.0"`
- `.devcontainer/devcontainer.json` → Node 20 feature
- `setup.sh` → Node 20.x installation

⚠️ **Current Environment** - Running Node v18.19.1 (needs rebuild)

## Solution: Rebuild Devcontainer

### Option 1: Rebuild in VS Code (Recommended)

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Select: **"Dev Containers: Rebuild Container"**
3. Wait for rebuild to complete (~5-10 minutes)
4. Verify Node version:

   ```bash
   node --version  # Should show v20.x.x
   ```

### Option 2: Rebuild from Command Line

```bash
# From your local machine (not in the container)
cd /path/to/space_hulk_game
docker compose -f .devcontainer/docker-compose.yml down
docker compose -f .devcontainer/docker-compose.yml up -d --build
```

### Option 3: Manual Node Upgrade (If Not Using Devcontainer)

```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version  # Should show v20.x.x
npm --version   # Should show v10.x.x
```

## After Upgrade

Once Node 20 is installed, reinstall frontend dependencies:

```bash
cd /home/devcontainers/space_hulk_game/frontend
rm -rf node_modules package-lock.json
npm install
```

Then verify tests work:

```bash
cd /home/devcontainers/space_hulk_game/frontend
rm -rf node_modules package-lock.json
npm install
```

## Verification

Run this command to verify your environment:

```bash
cd /home/devcontainers/space_hulk_game
./verify-node.sh
```

## Why This Happened

The devcontainer was configured for Node 20 (`.devcontainer/devcontainer.json` line 8), but the container needs to be rebuilt for the configuration to take effect. The container is currently running with an older image that had Node 18.

## Files Updated

- ✅ `.nvmrc` - Node version for nvm users
- ✅ `frontend/.nvmrc` - Frontend-specific Node version
- ✅ `frontend/package.json` - Added `engines` field
- ✅ `.devcontainer/devcontainer.json` - Already had Node 20
- ✅ `setup.sh` - Already had Node 20.x setup

## Next Steps

1. Rebuild the devcontainer using Option 1 above
2. Run `npm install` in frontend directory
3. Run `npm test` to verify tests pass

---

**Note**: The backend (Python) tests are unaffected and work perfectly with 186 tests passing.
