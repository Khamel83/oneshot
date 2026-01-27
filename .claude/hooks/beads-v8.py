#!/usr/bin/env python3
"""Compressed beads context (v8) - JSON not prose"""
import json
import subprocess
import os

def main():
    ctx = {"proto": "git", "end": ["status","add","sync","commit","sync","push"]}

    try:
        r = subprocess.run(['bd', 'ready', '--json'], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            ctx['ready'] = json.loads(r.stdout or '[]')[:3]
    except:
        ctx['ready'] = []

    print(json.dumps({"hookSpecificOutput": {"additionalContext": f"BEADS:{json.dumps(ctx, separators=(',', ':'))}"}}))

if __name__ == '__main__':
    main()
