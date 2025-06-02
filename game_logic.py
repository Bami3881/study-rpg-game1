import json
import os

def create_profile(player_class):
    return {
        'class': player_class,
        'level': 1,
        'xp': 0,
        'gold': 0,
        'inventory': {'Free Time Pass': 0, 'Rest Token': 0, 'Focus Potion': 0},
        'total_study_minutes': 0,
        'subject_totals': {},
        'level_xp_threshold': 1000
    }

def show_status(profile):
    st = __import__('streamlit')
    st.markdown(f"**🧪 Class:** {profile['class']}")
    st.markdown(f"**🏆 Level:** {profile['level']} ({profile['xp']}/{profile['level_xp_threshold']} XP)")
    st.markdown(f"**💰 Gold:** {profile['gold']}")
    st.markdown("**🎒 Inventory:**")
    for item, qty in profile['inventory'].items():
        st.markdown(f"- {item}: {qty}")
    st.markdown("**⏱️ Study Totals:**")
    for subj, mins in profile['subject_totals'].items():
        st.markdown(f"- {subj}: {mins} minutes")

def simulate_study(profile, minutes, subject):
    xp_gain = minutes * 10
    gold_gain = minutes * 5
    profile['xp'] += xp_gain
    profile['gold'] += gold_gain
    profile['total_study_minutes'] += minutes
    profile['subject_totals'][subject] = profile['subject_totals'].get(subject, 0) + minutes

    while profile['xp'] >= profile['level_xp_threshold']:
        profile['xp'] -= profile['level_xp_threshold']
        profile['level'] += 1
        profile['level_xp_threshold'] = int(profile['level_xp_threshold'] * 1.5)

def visit_shop(profile):
    st = __import__('streamlit')
    item_prices = {'Free Time Pass': 100, 'Rest Token': 75, 'Focus Potion': 50}
    for item, price in item_prices.items():
        if st.button(f"Buy {item} ({price} gold)"):
            if profile['gold'] >= price:
                profile['gold'] -= price
                profile['inventory'][item] += 1
                st.success(f"Purchased {item}!")
            else:
                st.error("Not enough gold!")

def save_profile(profile, path="data.json"):
    with open(path, "w") as f:
        json.dump(profile, f)

def load_profile(path="data.json"):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return create_profile("Biotech Alchemist")
