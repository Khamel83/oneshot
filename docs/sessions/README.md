# Encrypted Session Logs

Every Claude Code session is automatically saved here as an encrypted `.md.age` file.

## Decrypt

```bash
age --decrypt -i ~/.age/identity.txt session.md.age
```

## Setup (one-time)

If you don't have `~/.age/identity.txt`, you need to import the private key that matches the public key `age1kwu32vl7x3tx7dqphzykcf5cahgm4ejztm865f22fkwe5j6hwalqh0rau8`.

The private key format is:
```
AGE-SECRET-KEY-1...
```

## View all sessions

```bash
ls -t *.age | head -5
```

## Search encrypted sessions

```bash
# Decrypt all to temp, grep, clean up
for f in *.age; do age -d -i ~/.age/identity.txt "$f" 2>/dev/null | grep -q "SEARCH_TERM" && echo "$f"; done
```
