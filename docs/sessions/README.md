# Encrypted Session Logs

Every Claude Code session is automatically saved here as an encrypted `.md.age` file.

## Quick Commands

```bash
# List recent sessions
ls -t *.age | head -5

# View most recent (auto-decrypts)
age -d -i /home/ubuntu/.age/key.txt $(ls -t *.age | head -1)

# Search for a term
for f in *.age; do age -d -i /home/ubuntu/.age/key.txt "$f" 2>/dev/null | grep -q "TERM" && echo "$f"; done
```

Or use `/sessions` command in Claude Code.
