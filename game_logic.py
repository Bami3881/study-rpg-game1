import json
import os
import time
import random
from datetime import datetime, timedelta

# --------- Profile and Persistence ---------
def create_profile(name, player_class, picture_bytes):
    return {
        'name': name,
        'class': player_class,
        'picture': picture_bytes,
        'level': 1,
        'xp': 0,
        'gold': 0,
        'items': {},
        'stats': {
            'strength': 5,
            'dexterity': 5,
            'endurance': 5,
            'intelligence': 5
        },
        'stat_points': 0,
        'inventory': {'Free Time Pass': 0, 'Rest Token': 0, 'Focus Potion': 0},
        'total_study_minutes': 0,
        'subject_totals': {},
        'level_xp_threshold': 1000,
        'sessions': [],
        'timer_running': False,
        'timer_start': None,
        'timer_duration': None
    }

def save_profile(profile, path="data.json"):
    out = {
        'name': profile['name'],
        'class': profile['class'],
        'picture': profile['picture'].decode('latin1'),
        'level': profile['level'],
        'xp': profile['xp'],
        'gold': profile['gold'],
        'items': profile['items'],
        'stats': profile['stats'],
        'stat_points': profile.get('stat_points', 0),
        'inventory': profile['inventory'],
        'total_study_minutes': profile['total_study_minutes'],
        'subject_totals': profile['subject_totals'],
        'level_xp_threshold': profile['level_xp_threshold'],
        'sessions': [(dt.isoformat(), m) for dt, m in profile['sessions']],
    }
    with open(path, "w", encoding='latin1') as f:
        json.dump(out, f)

def load_profile(path="data.json"):
    if not os.path.exists(path):
        return None

    try:
        raw = open(path, "r", encoding="latin1").read()
        data = json.loads(raw)
        required_keys = [
            'name', 'class', 'picture', 'level', 'xp', 'gold',
            'items', 'stats', 'inventory', 'total_study_minutes',
            'subject_totals', 'level_xp_threshold', 'sessions'
        ]
        for key in required_keys:
            if key not in data:
                return None

        profile = {
            'name': data['name'],
            'class': data['class'],
            'picture': data['picture'].encode('latin1'),
            'level': data['level'],
            'xp': data['xp'],
            'gold': data['gold'],
            'items': data['items'],
            'stats': data['stats'],
            'stat_points': data.get('stat_points', 0),
            'inventory': data['inventory'],
            'total_study_minutes': data['total_study_minutes'],
            'subject_totals': data['subject_totals'],
            'level_xp_threshold': data['level_xp_threshold'],
            'sessions': [(datetime.fromisoformat(dt), m) for dt, m in data['sessions']],
            'timer_running': False,
            'timer_start': None,
            'timer_duration': None
        }
        return profile
    except Exception:
        return None

# --------- Leveling & Stats ---------
def add_xp(profile, amount):
    profile['xp'] += amount
    while profile['xp'] >= profile['level_xp_threshold']:
        profile['xp'] -= profile['level_xp_threshold']
        profile['level'] += 1
        profile['level_xp_threshold'] = int(profile['level_xp_threshold'] * 1.2)
        profile['stat_points'] = profile.get('stat_points', 0) + 2

def upgrade_stat(profile, stat_name):
    if profile['stat_points'] > 0 and stat_name in profile['stats']:
        profile['stats'][stat_name] += 1
        profile['stat_points'] -= 1
        return True
    return False

def simulate_study(profile, minutes, subject):
    xp_gain = minutes * 10
    gold_gain = minutes * 5
    if profile['class'] == "Arcanist of Algebra" and "Math" in subject:
        xp_gain = int(xp_gain * 1.1)
    if profile['class'] == "Biotech Alchemist" and subject in ["Campbell Biology", "AMC Math", "AP Seminar", "Pre-calculus", "NMSQT", "Psychology"]:
        gold_gain = int(gold_gain * 1.1)
    add_xp(profile, xp_gain)
    profile['gold'] += gold_gain
    profile['total_study_minutes'] += minutes
    profile['subject_totals'][subject] = profile['subject_totals'].get(subject, 0) + minutes
    profile['sessions'].append((datetime.now(), minutes))
    profile['inventory']['Rest Token'] += minutes // 60

def get_weekly_data(profile):
    today = datetime.now().date()
    daily = {today - timedelta(days=i): 0 for i in range(7)}
    for dt, m in profile['sessions']:
        d = dt.date()
        if d in daily:
            daily[d] += m
    dates = sorted(daily.keys())
    values = [daily[d] for d in dates]
    return dates, values

# --------- Shop & Gacha ---------
GACHA_POOL = [
    {"name": "Common Potion",       "type": "consumable", "effect": "Focus Potion",       "chance": 0.5},
    {"name": "Minor Gauntlets",     "type": "armor",      "stats": {"strength": 3},       "chance": 0.3},
    {"name": "Leather Boots",       "type": "armor",      "stats": {"dexterity": 3},      "chance": 0.15},
    {"name": "Enduring Medal",      "type": "artifact",   "stats": {"endurance": 5},      "chance": 0.04},
    {"name": "Mind Crown",          "type": "artifact",   "stats": {"intelligence": 5},   "chance": 0.01},
]

def gacha_spin(profile):
    cost = 50
    if profile['gold'] < cost:
        return None, "Not enough gold!"
    profile['gold'] -= cost
    roll = random.random()
    cumulative = 0.0
    for item in GACHA_POOL:
        cumulative += item['chance']
        if roll <= cumulative:

