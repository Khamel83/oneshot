# Encrypted Session Logs

Every Claude Code session is automatically saved here.

- **Full sessions**: `*.md.age` (encrypted with age)
- **Search index**: `index.md` (unencrypted, safe to commit)

## Quick Commands

```bash
# Search the index (no decryption needed)
cat index.md | grep "TOPIC"

# View most recent session (auto-decrypts)
age -d -i /home/ubuntu/.age/key.txt $(ls -t *.age | head -1)

# List recent sessions
ls -t *.age | head -5
```

Or use `/sessions` command in Claude Code.
