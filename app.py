import streamlit as st
import time
import pandas as pd
from datetime import datetime
from game_logic import *

# Set page configuration
st.set_page_config(page_title="Chronicles of Cerebria", page_icon="🧪", layout="wide")

# -------------- Initialization --------------
def initialize():
    profile = load_profile()
    if profile is None:
        profile = create_new_profile()
        save_profile(profile)
    st.session_state["profile"] = profile
    st.session_state["initialized"] = True

if "initialized" not in st.session_state:
    initialize()

profile = st.session_state["profile"]

# -------------- Sidebar Navigation --------------
pages = ["Home", "Study", "Stats", "Shop", "Adventure"]
choice = st.sidebar.radio("Navigation", pages)

# --------- Home Page ---------
if choice == "Home":
    st.header(f"Welcome, {profile['name']} the {profile['class']}!")
    if profile['picture']:
        st.image(profile['picture'], width=150)
    st.write(f"Level: {profile['level']} ({profile['xp']}/{profile['level_xp_threshold']} XP)")
    st.write(f"Gold: {profile['gold']}")
    st.write("Stats:")
    st.write(f"- Attack: {profile['stats']['attack']}")
    st.write(f"- Defense: {profile['stats']['defense']}")
    st.write(f"- Intelligence: {profile['stats']['intelligence']}")

# --------- Study Page ---------
elif choice == "Study":
    st.header("\ud83d\udcda Study Session")
    default_subjects = ["Campbell Biology", "AMC Math", "AP Seminar", "Pre-calculus", "NMSQT", "Psychology"]
    subject = st.selectbox("Select Subject", default_subjects + ["Add new..."])

    if subject == "Add new...":
        custom = st.text_input("Enter new subject name")
        if st.button("Add Subject") and custom:
            subject = custom
            default_subjects.append(custom)

    minutes = st.number_input("Set Timer (minutes)", min_value=5, max_value=180, value=30)

    if not profile.get("timer_running", False) and not profile.get("paused_time"):
        if st.button("Start Timer"):
            profile['timer_start'] = time.time()
            profile['timer_duration'] = minutes * 60
            profile['timer_running'] = True
            save_profile(profile)
            st.rerun()

    elif profile.get("timer_running"):
        elapsed = time.time() - profile['timer_start']
        remaining = max(int(profile['timer_duration'] - elapsed), 0)

        st.subheader(f"Time Remaining: {remaining//60:02d}:{remaining%60:02d}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Pause"):
                profile["paused_time"] = elapsed
                profile["timer_running"] = False
                save_profile(profile)
                st.rerun()
        with col2:
            if st.button("Stop Early"):
                if elapsed >= 600:
                    proportion = elapsed / profile["timer_duration"]
                    xp_gain, gold_gain = reward_study(proportion, minutes)
                    profile["xp"] += xp_gain
                    profile["gold"] += gold_gain
                    st.success(f"Session stopped early. You gained {xp_gain} XP and {gold_gain} gold.")
                else:
                    st.warning("Session stopped early, but no rewards were given.")
                profile.update({"timer_running": False, "timer_start": None, "timer_duration": None, "paused_time": None})
                save_profile(profile)
                st.rerun()

    elif profile.get("paused_time") is not None:
        paused_remaining = max(int(profile['timer_duration'] - profile['paused_time']), 0)
        st.subheader(f"Paused at: {paused_remaining//60:02d}:{paused_remaining%60:02d}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Resume"):
                profile["timer_start"] = time.time() - profile["paused_time"]
                profile["timer_running"] = True
                profile.pop("paused_time", None)
                save_profile(profile)
                st.rerun()
        with col2:
            if st.button("Stop Early"):
                if profile["paused_time"] >= 600:
                    proportion = profile["paused_time"] / profile["timer_duration"]
                    xp_gain, gold_gain = reward_study(proportion, minutes)
                    profile["xp"] += xp_gain
                    profile["gold"] += gold_gain
                    st.success(f"Session stopped early. You gained {xp_gain} XP and {gold_gain} gold.")
                else:
                    st.warning("Session stopped early, but no rewards were given.")
                profile.update({"timer_running": False, "timer_start": None, "timer_duration": None})
                profile.pop("paused_time", None)
                save_profile(profile)
                st.rerun()

    elif profile.get("timer_start") and not profile.get("timer_running"):
        elapsed = time.time() - profile['timer_start']
        if elapsed >= profile['timer_duration']:
            st.subheader("\ud83d\udd14 Time's up! Click below to complete session.")
            if st.button("Complete Session"):
                simulate_study(profile, int(profile['timer_duration'] / 60), subject)
                profile.update({"timer_running": False, "timer_start": None, "timer_duration": None})
                save_profile(profile)
                st.success("Session recorded! Check Stats page for details.")
                st.rerun()

# --------- Stats Page ---------
elif choice == "Stats":
    st.header("\ud83d\udcca Study Statistics")
    st.write(f"Total Study Time: {profile['total_study_minutes']} minutes")
    st.write("By Subject:")

    for subj, mins in profile['subject_totals'].items():
        st.write(f"- {subj}: {mins} minutes")

    dates, values = get_weekly_data(profile)
    df = pd.DataFrame({'Date': dates, 'Minutes': values})
    df = df.set_index('Date')
    st.line_chart(df)

# --------- Shop Page ---------
elif choice == "Shop":
    st.header("\ud83d\udecd\ufe0f Merchant’s Shop")
    st.write(f"You have {profile['gold']} gold.")
    st.write("Gacha Spin: 50 gold per spin (chance to win random items)")
    if st.button("Spin Gacha"):
        item, msg = gacha_spin(profile)
        if item:
            st.success(msg)
        else:
            st.error(msg)
        save_profile(profile)

    st.write("Your Items:")
    for item_name, qty in profile['items'].items():
        st.write(f"- {item_name} (x{qty})")
        if st.button(f"Sell One {item_name}"):
            success, message = sell_item(profile, item_name)
            if success:
                st.success(message)
            else:
                st.error(message)
            save_profile(profile)

# --------- Adventure Page ---------
elif choice == "Adventure":
    st.header("\u2694\ufe0f Boss Raid")
    st.write("Test your might against the Boss!")
    if st.button("Challenge Boss"):
        win, message = boss_raid(profile)
        if win:
            st.success(message)
        else:
            st.error(message)
        save_profile(profile)

