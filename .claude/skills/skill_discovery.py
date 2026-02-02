#!/usr/bin/env python3
"""
ONE_SHOT v9 Skill Discovery

Automatically matches skills to user goals.
Supports local skills and SkillsMP integration.
"""

import json
import os
import re
import subprocess
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
from urllib.parse import quote

# Load skills inventory
INVENTORY_PATH = Path("/home/ubuntu/github/oneshot/.claude/skills_inventory.json")

def load_inventory():
    """Load skills inventory from JSON."""
    with open(INVENTORY_PATH) as f:
        return json.load(f)

def match_skills_to_goal(goal, inventory=None):
    """
    Match skills to a user goal using keyword matching.

    Args:
        goal: User's goal/description (string)
        inventory: Skills inventory (list of dicts)

    Returns:
        List of matching skills with relevance scores
    """
    if inventory is None:
        inventory = load_inventory()

    # Extract keywords from goal
    goal_words = set(re.findall(r'\w+', goal.lower()))

    matches = []
    for skill in inventory:
        score = 0
        desc = skill['description'].lower()
        name = skill['name'].lower()

        # Check for keyword matches in description
        for word in goal_words:
            if word in desc:
                score += 1
            if word in name:
                score += 2  # Name matches worth more

        if score > 0:
            matches.append({
                **skill,
                'relevance_score': score
            })

    # Sort by relevance score
    matches.sort(key=lambda x: x['relevance_score'], reverse=True)
    return matches

def find_skill_gaps(goal, inventory=None):
    """
    Identify skill gaps - things the goal needs that we don't have skills for.

    Args:
        goal: User's goal
        inventory: Skills inventory

    Returns:
        List of suggested SkillsMP searches
    """
    # Common skill categories and their keywords
    categories = {
        'database': ['database', 'db', 'sql', 'postgres', 'mysql', 'mongodb', 'data store'],
        'api': ['api', 'rest', 'graphql', 'endpoint', 'http'],
        'auth': ['auth', 'login', 'authentication', 'oauth', 'jwt', 'security'],
        'testing': ['test', 'testing', 'spec', 'coverage', 'pytest', 'jest'],
        'deployment': ['deploy', 'deployment', 'ci', 'cd', 'release', 'ship'],
        'documentation': ['doc', 'readme', 'documentation', 'wiki'],
        'monitoring': ['monitor', 'metrics', 'logging', 'observability', 'alert'],
        'frontend': ['frontend', 'ui', 'react', 'vue', 'angular', 'css', 'html'],
        'backend': ['backend', 'server', 'api', 'service'],
        'blockchain': ['blockchain', 'web3', 'smart contract', 'crypto', 'nft', 'defi'],
        'cli': ['cli', 'command line', 'terminal', 'shell script'],
        'mobile': ['mobile', 'ios', 'android', 'app', 'react native', 'flutter'],
    }

    if inventory is None:
        inventory = load_inventory()

    # What we have
    have_keywords = set()
    for skill in inventory:
        have_keywords.update(re.findall(r'\w+', skill['description'].lower()))

    # What we need (based on goal)
    gaps = []
    goal_lower = goal.lower()

    for category, keywords in categories.items():
        if any(kw in goal_lower for kw in keywords):
            # Check if we have coverage
            if not any(kw in have_keywords for kw in keywords):
                gaps.append({
                    'category': category,
                    'suggested_search': f"{category} skill"
                })

    return gaps


# ============ SkillsMP Integration ============

SKILLSMP_API_BASE = "https://skillsmp.com/api/v1"
SKILLSMP_API_KEY = os.environ.get("SKILLSMP_API_KEY", "")


def search_skillsmp(query, limit=5, use_ai_search=False):
    """
    Search SkillsMP for skills matching a query.

    Args:
        query: Search query string
        limit: Max results to return
        use_ai_search: Use AI semantic search instead of keyword search

    Returns:
        List of skill dicts from SkillsMP, or None if API unavailable
    """
    if not SKILLSMP_API_KEY:
        return None  # No API key configured

    if not HAS_REQUESTS:
        print("⚠️  requests library not installed. Install with: pip install requests")
        return None

    endpoint = "/skills/ai-search" if use_ai_search else "/skills/search"

    try:
        response = requests.get(
            f"{SKILLSMP_API_BASE}{endpoint}",
            params={"q": query, "limit": limit},
            headers={"Authorization": f"Bearer {SKILLSMP_API_KEY}"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            return data.get("data", {}).get("skills", [])
        else:
            error = data.get("error", {})
            print(f"⚠️  SkillsMP API error: {error.get('code', 'unknown')}")
            return None
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            print(f"⚠️  SkillsMP API key invalid or expired.")
        else:
            print(f"⚠️  SkillsMP API error: {e.response.status_code}")
        return None
    except Exception as e:
        print(f"⚠️  SkillsMP error: {e}")
        return None


def install_skillsmp_skill(skill_name):
    """
    Install a skill from SkillsMP using Claude Code CLI.

    Args:
        skill_name: Skill name or identifier (e.g., "cli-designer")

    Returns:
        True if successful, False otherwise
    """
    try:
        # Use Claude Code's plugin install command
        result = subprocess.run(
            ["claude", "plugin", "install", f"{skill_name}@skillsmp"],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("⚠️  Claude CLI not found. Cannot install SkillsMP skill.")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Installation timed out.")
        return False
    except Exception as e:
        print(f"⚠️  Installation failed: {e}")
        return False


def recommend_skills(goal, limit=5, use_skillsmp=False):
    """
    Recommend skills for a given goal.

    Args:
        goal: User's goal
        limit: Max number of recommendations
        use_skillsmp: Whether to search SkillsMP for gaps

    Returns:
        Dict with local_skills, skill_gaps, and skillsmp_results
    """
    inventory = load_inventory()

    # Find local matches
    local_matches = match_skills_to_goal(goal, inventory)[:limit]

    # Find gaps
    gaps = find_skill_gaps(goal, inventory)

    # Search SkillsMP if requested and gaps found
    skillsmp_results = []
    if use_skillsmp and gaps:
        for gap in gaps[:3]:  # Limit SkillsMP searches
            results = search_skillsmp(gap['suggested_search'], limit=3)
            if results:
                skillsmp_results.extend(results)

    return {
        'goal': goal,
        'local_skills': local_matches,
        'skill_gaps': gaps,
        'skillsmp_results': skillsmp_results,
        'total_local_found': len(local_matches),
        'gaps_identified': len(gaps),
        'skillsmp_available': len(skillsmp_results)
    }

# CLI interface
if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Discover ONE_SHOT skills for a given goal"
    )
    parser.add_argument("goal", nargs="+", help="Your goal or task description")
    parser.add_argument(
        "--skillsmp", "-s",
        action="store_true",
        help="Search SkillsMP for skill gaps (requires SKILLSMP_API_KEY)"
    )
    parser.add_argument(
        "--ai-search",
        action="store_true",
        help="Use SkillsMP AI semantic search (requires --skillsmp)"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=5,
        help="Max results per category (default: 5)"
    )
    args = parser.parse_args()

    goal = ' '.join(args.goal)

    print(f"🔍 Analyzing goal: {goal}\n")

    result = recommend_skills(
        goal,
        limit=args.limit,
        use_skillsmp=args.skillsmp
    )

    print(f"📦 Local skills found: {result['total_local_found']}\n")
    for skill in result['local_skills']:
        print(f"  ✅ {skill['name']}: {skill['description'][:60]}...")
        print(f"     Relevance: {skill['relevance_score']} | Lines: {skill['lines']}")
        print()

    if result['gaps_identified'] > 0:
        print(f"🔍 Potential skill gaps: {result['gaps_identified']}\n")
        for gap in result['skill_gaps']:
            print(f"  ⚠️  {gap['category']}: Consider searching SkillsMP for '{gap['suggested_search']}'")
        print()

        if args.skillsmp and result['skillsmp_available'] > 0:
            print(f"🌐 SkillsMP results: {result['skillsmp_available']}\n")
            for skill in result['skillsmp_results']:
                name = skill.get('name', 'Unknown')
                desc = skill.get('description', '')[:60]
                author = skill.get('author', 'Unknown')
                print(f"  🔷 {name} by @{author}")
                print(f"     {desc}...")
                print()
        elif args.skillsmp:
            print("ℹ️  No SkillsMP results found (check API key or search terms)\n")
    else:
        print("✅ No obvious skill gaps identified!\n")
