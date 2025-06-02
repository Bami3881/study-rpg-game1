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
    st.header("📚 Study Session")
    default_subjects = ["Campbell Biology", "AMC Math", "AP Seminar", "Pre-calculus", "NMSQT", "Psychology"]
    subject = st.selectbox("Select Subject", default_subjects + ["Add new..."])
    if subject == "Add new...":
        custom = st.text_input("Enter new subject name")
        if st.button("Add Subject") and custom:
            subject = custom
            default_subjects.append(custom)

    minutes = st.number_input("Set Timer (minutes)", min_value=5, max_value=180, value=30)
    if not profile.get("timer_running", False):
        if st.button("Start Timer"):
            profile['timer_start'] = time.time()
            profile['timer_duration'] = minutes * 60
            profile['timer_running'] = True
            save_profile(profile)
            st.experimental_rerun()
    else:
        elapsed = time.time() - profile['timer_start']
remaining = int(profile['timer_duration'] - elapsed)

if remaining > 0:
    mins, secs = divmod(remaining, 60)
    st.subheader(f"Time Remaining: {mins:02d}:{secs:02d}")
    
    # Trigger rerun after rendering with a short delay
    st.session_state["_rerun_trigger"] = True
    time.sleep(1)
    st.experimental_rerun()
else:
    st.subheader("🔔 Time's up! Click below to complete session.")
    if st.button("Complete Session"):
        simulate_study(profile, int(profile['timer_duration'] / 60), subject)
        profile['timer_running'] = False
        profile['timer_start'] = None
        profile['timer_duration'] = None
        save_profile(profile)
        st.success("Session recorded! Check Stats page for details.")
        st.session_state["_rerun_trigger"] = False  # reset rerun flag
        st.experimental_rerun()

# --------- Stats Page ---------
elif choice == "Stats":
    st.header("📊 Study Statistics")
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
    st.header("🛍️ Merchant’s Shop")
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
    st.header("⚔️ Boss Raid")
    st.write("Test your might against the Boss!")
    if st.button("Challenge Boss"):
        win, message = boss_raid(profile)
        if win:
            st.success(message)
        else:
            st.error(message)
        save_profile(profile)
