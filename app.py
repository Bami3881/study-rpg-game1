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
choice = st.sidebar.radio("Navigation", pages, key="navigation_radio")

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
    subject = st.selectbox("Select Subject", default_subjects + ["Add new..."], key="subject_select")

    if subject == "Add new...":
        custom = st.text_input("Enter new subject name", key="custom_subject_input")
        if st.button("Add Subject", key="add_subject_button") and custom:
            subject = custom
            default_subjects.append(custom)

    minutes = st.number_input("Set Timer (minutes)", min_value=5, max_value=180, value=30, key="timer_input")

    if not profile.get("timer_running", False):
        if st.button("Start Timer", key="start_timer_button"):
            profile['timer_start'] = time.time()
            profile['timer_duration'] = minutes * 60
            profile['timer_running'] = True
            save_profile(profile)
if profile:
    st.write("Profile loaded successfully!")
if condition1:
    print("Condition met")
elif condition2:
    print("Another case")
else:  # ✅ Properly aligned
    print("Default case executed")

        
        elapsed = time.time() - profile['timer_start']
        remaining = int(profile['timer_duration'] - elapsed)

        if remaining > 0:
            mins, secs = divmod(remaining, 60)
            st.subheader(f"Time Remaining: {mins:02d}:{secs:02d}")

            # Trigger rerun after rendering with a short delay
            st.session_state["_rerun_trigger"] = True
            
        else:
            st.subheader("🔔 Time's up! Click below to complete session.")
            if st.button("Complete Session", key="complete_session_button"):
                simulate_study(profile, int(profile['timer_duration'] / 60), subject)
                profile['timer_running'] = False
                profile['timer_start'] = None
                profile['timer_duration'] = None
                save_profile(profile)
                st.success("Session recorded! Check Stats page for details.")
                st.session_state["_rerun_trigger"] = False  # reset rerun flag
                if profile

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
    
    if st.button("Spin Gacha", key="spin_gacha_button"):
        item, msg = gacha_spin(profile)
        if item:
            st.success(msg)
        else:
            st.error(msg)
        save_profile(profile)

    st.write("Your Items:")
    for item_name, qty in profile['items'].items():
        st.write(f"- {item_name} (x{qty})")
        if st.button(f"Sell One {item_name}", key=f"sell_{item_name}_button"):
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
    
    if st.button("Challenge Boss", key="challenge_boss_button"):
        win, message = boss_raid(profile)
        if win:
            st.success(message)
        else:
            st.error(message)
        save_profile(profile)

# --------- Timer Controls ---------
if choice == "Study":
    if profile.get("timer_running", False):
        st.write(f"Timer Running: {profile.get('timer_running')}")
        st.write(f"Paused Time: {profile.get('paused_time', 'Not set')}")
        st.write(f"Remaining Time: {remaining}")  # 🔹 Add here for debugging
        
        elapsed = time.time() - profile["timer_start"]
        remaining = max(int(profile["timer_duration"] - elapsed), 0)

        st.subheader(f"Time Remaining: {remaining//60:02d}:{remaining%60:02d}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Pause", key="pause_button"):
                profile["timer_running"] = False
                profile["paused_time"] = elapsed
                if profile
        with col2:
            if st.button("Stop Early", key="stop_button"):
                if elapsed >= 600:  # More than 10 minutes
                    proportion = elapsed / profile["timer_duration"]
                    profile["xp"] += int(proportion * 10 * (minutes))
                    profile["gold"] += int(proportion * 5 * (minutes))
                    st.success(f"Session stopped early. You gained {profile['xp']} XP and {profile['gold']} gold.")
                else:
                    st.warning("Session stopped early, but no rewards were given.")

                profile["timer_running"] = False
                profile["timer_start"] = None
                profile["timer_duration"] = None
                profile["paused_time"] = None
                st.rerun()

    elif "paused_time" in profile and profile["paused_time"] is not None:
        paused_remaining = max(int(profile["timer_duration"] - profile["paused_time"]), 0)
        st.subheader(f"Paused at: {paused_remaining//60:02d}:{paused_remaining%60:02d}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Resume", key="resume_button"):
                profile["timer_running"] = True
                profile["timer_start"] = time.time() - profile["paused_time"]
                del profile["paused_time"]
                st.rerun()
        with col2:
            if st.button("Stop Early", key="stop_after_pause_button"):
                if profile["paused_time"] >= 600:  # More than 10 minutes
                    proportion = profile["paused_time"] / profile["timer_duration"]
                    profile["xp"] += int(proportion * 10 * (minutes))
                    profile["gold"] += int(proportion * 5 * (minutes))
                    st.success(f"Session stopped early. You gained {profile['xp']} XP and {profile['gold']} gold.")
                else:
                    st.warning("Session stopped early, but no rewards were given.")

                profile["timer_running"] = False
                profile["timer_start"] = None
                profile["timer_duration"] = None
                del profile["paused_time"]
                st.rerun()
