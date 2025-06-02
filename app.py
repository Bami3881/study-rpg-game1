import streamlit as st
from game_logic import *

st.set_page_config(page_title="Chronicles of Cerebria", page_icon="🧪")
st.title("🧪 Chronicles of Cerebria")
st.subheader("Your Study RPG")

if 'profile' not in st.session_state:
    st.session_state.profile = create_profile("Biotech Alchemist")

show_status(st.session_state.profile)

st.markdown("---")
with st.form("study_form"):
    subject = st.text_input("Subject", value="Biology")
    minutes = st.number_input("Study Duration (minutes)", min_value=5, max_value=180, value=30)
    submitted = st.form_submit_button("📚 Simulate Study")

if submitted:
    simulate_study(st.session_state.profile, minutes, subject)
    st.success(f"Studied {minutes} minutes of {subject}!")
    show_status(st.session_state.profile)

st.markdown("### 🛍️ Shop")
if st.button("Visit Shop"):
    visit_shop(st.session_state.profile)

save_profile(st.session_state.profile)
