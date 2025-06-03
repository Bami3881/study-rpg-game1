# -*- coding: utf-8 -*-
import streamlit as st
import time
import pandas as pd
from datetime import datetime
from game_logic import *

# Set page configuration (no emoji in page icon)
st.set_page_config(page_title="Chronicles of Cerebria", page_icon="🔬", layout="wide")

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
    st.header("Study Session")
    default_subjects = ["Campbell Biology", "AMC Math", "AP Seminar", "Pre-calculus", "NMSQT", "Psychology"]
    subject = st.selectbox("Select Subject", default_subjects + ["Add new..."])

    if subject == "Add new...":
        custom = st.text_input("Enter new subject name")
        if st.button("Add Subject") and custom:
            subject = custom
            default_subjects.append(custom)

    minutes = st.number_input("Set Timer (minutes)", min_value=5, max_value=180, value=30, key="study_timer_input")

    if not profile.get("timer_running", False) and not profile.get("paused_time"):
        if st.button("Start Timer"):
            profile['timer_start'] = time.time()
            profile['timer_duration'] = minutes * 60
            profile['timer_running'] = True
            profile['current_subject'] = subject
            save_profile(profile)
            st.rerun()

    elif profile.get("timer_running", False):
        elapsed = time.time() - profile['timer_start']
        remaining = int(profile['timer_duration'] - elapsed)

        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.subheader(f"Time Remaining: {mins:02d}:{secs:02d}")
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
                        proportion = elapsed / profile['timer_duration']
                        xp_earned = int(proportion * 10 * (profile['timer_duration'] / 60))
                        gold_earned = int(proportion * 5 * (profile['timer_duration'] / 60))
                        profile["xp"] += xp_earned
                        profile["gold"] += gold_earned
                        profile["total_study_minutes"] += int(elapsed / 60)
                        profile["subject_totals"][profile['current_subject']] = profile["subject_totals"].get(profile['current_subject'], 0) + int(elapsed / 60)
                        st.success(f"Session stopped early. You earned {xp_earned} XP and {gold_earned} gold.")
                    else:
                        st.warning("Studied less than 10 minutes. No rewards earned.")

                    profile["timer_running"] = False
                    profile["timer_start"] = None
                    profile["timer_duration"] = None
                    profile["paused_time"] = None
                    profile["current_subject"] = None
                    save_profile(profile)
                    st.rerun()

            time.sleep(1)
            st.rerun()
        else:
            st.subheader("Time's up! Click below to complete session.")
            if st.button("Complete Session"):
                simulate_study(profile, int(profile['timer_duration'] / 60), profile["current_subject"])
                profile["timer_running"] = False
                profile["timer_start"] = None
                profile["timer_duration"] = None
                profile["current_subject"] = None
                profile["paused_time"] = None
                save_profile(profile)
                st.success("Session recorded! Check Stats page for details.")
                st.rerun()

    elif profile.get("paused_time") is not None:
        paused_remaining = max(int(profile["timer_duration"] - profile["paused_time"]), 0)
        mins, secs = divmod(paused_remaining, 60)
        st.subheader(f"Paused at: {mins:02d}:{secs:02d}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Resume"):
                profile["timer_start"] = time.time() - profile["paused_time"]
                profile["timer_running"] = True
                profile["paused_time"] = None
                save_profile(profile)
                st.rerun()
        with col2:
            if st.button("Stop Early"):
                if profile["paused_time"] >= 600:
                    proportion = profile["paused_time"] / profile["timer_duration"]
                    xp_earned = int(proportion * 10 * (profile['timer_duration'] / 60))
                    gold_earned = int(proportion * 5 * (profile['timer_duration'] / 60))
                    profile["xp"] += xp_earned
                    profile["gold"] += gold_earned
                    profile["total_study_minutes"] += int(profile["paused_time"] / 60)
                    profile["subject_totals"][profile['current_subject']] = profile["subject_totals"].get(profile['current_subject'], 0) + int(profile["paused_time"] / 60)
                    st.success(f"Session stopped early. You earned {xp_earned} XP and {gold_earned} gold.")
                else:
                    st.warning("Studied less than 10 minutes. No rewards earned.")

                profile["timer_running"] = False
                profile["timer_start"] = None
                profile["timer_duration"] = None
                profile["paused_time"] = None
                profile["current_subject"] = None
                save_profile(profile)
                st.rerun()

# --------- Stats Page ---------
elif choice == "Stats":
    st.header("Study Statistics")  # Removed emoji
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
    st.header("Merchant’s Shop")  # Removed emoji
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
    st.header("Boss Raid")  # Removed emoji
    st.write("Test your might against the Boss!")
    if st.button("Challenge Boss"):
        win, message = boss_raid(profile)
        if win:
            st.success(message)
        else:
            st.error(message)
        save_profile(profile)

