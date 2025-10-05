# Installation Guide

Complete installation guide for Graphbrain with LLM integration.

## ⚠️ Important: LevelDB 1.22 Required

**Why LevelDB 1.22 specifically?**

LevelDB 1.23+ has **compatibility issues with plyvel** on Apple Silicon. You must install version 1.22 for stable operation.

## Recommended Installation: LevelDB 1.22

**For all users, we strongly recommend LevelDB 1.22** for optimal performance and stability.

---

## macOS (M1/M2/M3/M4) - Step by Step

**Important:** Follow these steps **one by one** (not all at once).

### Step 1: Create Homebrew tap for LevelDB 1.22

```bash
brew tap-new <your-username>/leveldb
```

Replace `<your-username>` with your actual username.

### Step 2: Navigate to tap directory

```bash
cd "$(brew --repo <your-username>/leveldb)"
```

### Step 3: Download LevelDB 1.22 formula

```bash
wget https://raw.githubusercontent.com/Homebrew/homebrew-core/e2c833d326c45d9aaf4e26af6dd8b2f31564dc04/Formula/leveldb.rb -O Formula/leveldb.rb
```

This downloads the exact formula for LevelDB 1.22 (the last compatible version with plyvel on Apple Silicon).

### Step 4: Install LevelDB 1.22

```bash
brew install <your-username>/leveldb/leveldb
```

### Step 5: Verify LevelDB version

```bash
brew list --versions leveldb
```

**Expected output:** `leveldb 1.22`

If you see 1.23 or higher, something went wrong. Uninstall and retry steps 1-4.

### Step 6: Configure environment variables (permanent)

```bash
echo 'export LIBRARY_PATH="$LIBRARY_PATH:/opt/homebrew/lib"' >> ~/.zshrc
echo 'export CPATH="$CPATH:/opt/homebrew/include"' >> ~/.zshrc
source ~/.zshrc
```

These variables tell plyvel where to find LevelDB 1.22.

### Step 7: Create virtual environment

```bash
python3 -m venv gcpu_env
source gcpu_env/bin/activate
```

### Step 8: Install Graphbrain

```bash
cd /path/to/graphbrain
pip install -e .
```

### Step 9: Install spaCy model

```bash
python -m spacy download en_core_web_lg
```

### Step 10: Test installation

```bash
python -c "import plyvel; print('✓ plyvel OK')"
python -c "from graphbrain import hgraph; hg = hgraph('test.hg'); print('✓ LevelDB OK'); hg.close()"
python -c "from graphbrain.api import GraphbrainAPI; print('✓ API OK')"
```

**Expected output:**
```
✓ plyvel OK
✓ LevelDB OK
✓ API OK
```

✅ **Done!** LevelDB 1.22 is now installed and working.

---

## macOS (Intel) - Step by Step

### Step 1: Install LevelDB via Homebrew

```bash
brew install leveldb
```

### Step 2: Check version

```bash
brew list --versions leveldb
```

If version is 1.23+, you need to use the tap method (Steps 1-4 from M-series section above).

### Step 3: Configure environment

```bash
export LIBRARY_PATH="$LIBRARY_PATH:/usr/local/lib"
export CPATH="$CPATH:/usr/local/include"
```

### Step 4: Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Graphbrain

```bash
pip install -e .
```

### Step 6: Install spaCy model

```bash
python -m spacy download en_core_web_lg
```

### Step 7: Test

```bash
python -c "from graphbrain.api import GraphbrainAPI; print('✓ OK')"
```

---

## Linux (Ubuntu/Debian) - Step by Step

### Step 1: Install system dependencies

```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev wget
```

### Step 2: Install LevelDB 1.22 from source

```bash
# Download LevelDB 1.22
cd /tmp
wget https://github.com/google/leveldb/archive/refs/tags/1.22.tar.gz
tar -xzf 1.22.tar.gz
cd leveldb-1.22

# Build and install
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release .. && cmake --build .
sudo cmake --build . --target install
sudo ldconfig
```

### Step 3: Verify installation

```bash
ldconfig -p | grep leveldb
```

Should show `libleveldb.so.1.22`.

### Step 4: Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 5: Install Graphbrain

```bash
pip install -e .
```

### Step 6: Install spaCy model

```bash
python -m spacy download en_core_web_lg
```

### Step 7: Test

```bash
python -c "import plyvel; print('✓ plyvel OK')"
python -c "from graphbrain.api import GraphbrainAPI; print('✓ API OK')"
```

---

## Windows

LevelDB installation on Windows is complex. **We recommend using SQLite backend** (see below).

If you must use LevelDB on Windows:

1. Install Visual Studio Build Tools
2. Use vcpkg to install LevelDB 1.22 (not 1.23+)
3. Configure environment variables

**For most Windows users:** Use SQLite backend instead.

---

## Alternative: SQLite Backend (Beta)

**Note:** SQLite backend is in **beta development**. LevelDB 1.22 is strongly recommended.

**Use SQLite only if:**
- You're on Windows and can't install LevelDB
- You're doing quick prototyping
- Your graph has < 100k edges

### Installation (SQLite)

```bash
# No system dependencies needed
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -e .
python -m spacy download en_core_web_lg
```

### Usage (SQLite)

```python
from graphbrain.api import GraphbrainAPI

# Use .db extension for SQLite
with GraphbrainAPI('my_graph.db') as api:
    api.add_fact('test', 'works', 'yes')
```

**SQLite Limitations:**
- ⚠️ Beta stability
- ⚠️ 5-10x slower than LevelDB
- ⚠️ Not recommended for production

---

## Backend Comparison

| Feature | LevelDB 1.22 (Recommended) | SQLite (Beta) |
|---------|---------------------------|---------------|
| **Performance** | ★★★★★ Fast | ★★★☆☆ Moderate |
| **Stability** | ★★★★★ Production | ★★★☆☆ Beta |
| **Installation** | Medium (worth it!) | Easy |
| **Best for** | All users | Windows fallback |
| **File extension** | `.hg` | `.db` |

**Recommendation:** Use LevelDB 1.22 for all scenarios. The installation takes 10 minutes but gives you production-grade performance.

---

## Troubleshooting

### Issue: plyvel compilation error

**Symptom:**
```
error: command 'gcc' failed with exit status 1
```

**Solution (macOS M-series):**

1. Check environment variables:
```bash
echo $LIBRARY_PATH
echo $CPATH
```

Should include `/opt/homebrew/lib` and `/opt/homebrew/include`.

2. Reinstall plyvel from source:
```bash
pip uninstall plyvel
pip install --no-binary :all: plyvel
```

### Issue: LevelDB version mismatch

**Symptom:**
```
ImportError: plyvel cannot find leveldb
```

**Solution:**

Check your LevelDB version:
```bash
brew list --versions leveldb
```

**Must be 1.22**. If it shows 1.23+:

```bash
brew uninstall leveldb
# Then follow Steps 1-4 from macOS M-series section
```

### Issue: Wrong architecture (M-series)

**Symptom:**
```
Mach-O file, but is an incompatible architecture
```

**Solution:**

Make sure you're using ARM64 Python:
```bash
python3 -c "import platform; print(platform.machine())"
```

Should show `arm64`, not `x86_64`.

If showing x86_64, reinstall Python for Apple Silicon.

### Issue: Permission denied

**Never use sudo with pip!**

```bash
# Use virtual environment instead
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

---

## Verification

After installation, test everything:

```bash
# Test plyvel
python -c "import plyvel; print('✓ plyvel installed')"

# Test LevelDB version compatibility
python -c "
import plyvel
db = plyvel.DB('/tmp/test_leveldb.db', create_if_missing=True)
db.put(b'test', b'ok')
assert db.get(b'test') == b'ok'
db.close()
import shutil
shutil.rmtree('/tmp/test_leveldb.db')
print('✓ LevelDB 1.22 working')
"

# Test Graphbrain
python -c "
from graphbrain import hgraph
hg = hgraph('test.hg')
hg.add('(is/P graphbrain/C awesome/C)')
print('✓ Graphbrain works')
hg.close()
"

# Test API
python -c "from graphbrain.api import GraphbrainAPI; print('✓ API module works')"
```

**All checks passed?** You're ready to go! 🎉

---

## Next Steps

Once installed:

1. ✅ Complete the [Quick Start](quickstart.md)
2. ✅ Run [examples](../examples/)
3. ✅ Read [features](features.md)

## Support

- **LevelDB 1.22 issues:** Follow steps exactly as written above
- **Still having issues:** Open a GitHub issue with your error message
- **Windows:** Use SQLite backend

---

## Quick Reference

**macOS M-series (most common):**
```bash
brew tap-new <your-username>/leveldb
cd "$(brew --repo <your-username>/leveldb)"
wget https://raw.githubusercontent.com/Homebrew/homebrew-core/e2c833d326c45d9aaf4e26af6dd8b2f31564dc04/Formula/leveldb.rb -O Formula/leveldb.rb
brew install <your-username>/leveldb/leveldb
echo 'export LIBRARY_PATH="$LIBRARY_PATH:/opt/homebrew/lib"' >> ~/.zshrc
echo 'export CPATH="$CPATH:/opt/homebrew/include"' >> ~/.zshrc
source ~/.zshrc
python3 -m venv gcpu_env && source gcpu_env/bin/activate
pip install -e .
python -m spacy download en_core_web_lg
```

Replace `<your-username>` with your actual username!

**Verify:**
```bash
brew list --versions leveldb  # Should show 1.22
python -c "import plyvel; print('✓')"
```

Done! 🎉
