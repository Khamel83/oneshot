#!/usr/bin/env python3
"""
ONE_SHOT v8: Ultra-compressed context hook
Single JSON dump, 2k tokens total (down from 20k).
"""
import json
import os
import subprocess

def main():
    # Skill router (top 10 only)
    skills = [
        ["build me|new project|/interview", "front-door"],
        ["plan|design|approach", "create-plan"],
        ["implement|execute|build it", "implement-plan"],
        ["bug|error|fix|debug|broken", "debugger"],
        ["review|check code|is this safe", "code-reviewer"],
        ["beads|ready tasks|what's next", "beads"],
        ["deploy|push to cloud|host this", "push-to-cloud"],
        ["handoff|save context|before clear", "create-handoff"],
        ["resume|continue|from handoff", "resume-handoff"],
        ["stuck|looping|confused|start over", "failure-recovery"]
    ]

    # Infrastructure
    infra = {
        "oci": "100.126.13.70",
        "home": "100.112.130.100",
        "mac": "100.113.216.27",
        "net": "Tailscale deer-panga.ts.net"
    }

    # Stacks
    stacks = {
        "web": "Convex+Next.js+Clerk->Vercel",
        "cli": "Python+Click+SQLite",
        "svc": "Python+systemd->oci"
    }

    # Beads status
    beads = {"ready": 0, "open": 0, "lessons": 0}
    tasks = []
    lessons = []
    project = {}

    try:
        # Get beads counts
        r = subprocess.run(['bd', 'list', '--status', 'open', '--json'],
                          capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            open_tasks = json.loads(r.stdout or '[]')
            beads['open'] = len(open_tasks)
            beads['ready'] = len([t for t in open_tasks if not t.get('blockedBy')])
            tasks = [{"id": t.get('id', ''), "t": t.get('title', '')[:30]}
                    for t in open_tasks[:5]]

        # Get lessons
        r = subprocess.run(['bd', 'list', '-l', 'lesson', '--json'],
                          cwd=os.path.expanduser('~/.claude'),
                          capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            lsns = json.loads(r.stdout or '[]')[:3]
            beads['lessons'] = len(lsns)
            lessons = [l.get('title', '')[:40] for l in lsns]

        # Project checks
        pd = os.environ.get('CLAUDE_PROJECT_DIR', '')
        if pd:
            project = {
                "b": os.path.exists(os.path.join(pd, '.beads')),
                "m": os.path.exists(os.path.join(pd, '.claude', 'CLAUDE.md')),
                "o": os.path.exists(os.path.join(pd, 'LLM-OVERVIEW.md')),
                "a": os.path.exists(os.path.join(pd, 'AGENTS.md'))
            }
    except:
        pass

    ctx = {
        "v": 8,
        "s": skills,
        "i": infra,
        "k": stacks,
        "b": beads,
        "t": tasks,
        "l": lessons,
        "p": project
    }

    print(json.dumps({"hookSpecificOutput": {"additionalContext": f"CTX:{json.dumps(ctx, separators=(',', ':'))}"}}))

if __name__ == '__main__':
    main()
