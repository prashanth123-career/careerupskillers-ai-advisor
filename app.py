# Form Logic with Progress Bar
if not st.session_state.completed:
    q, hint = questions[st.session_state.q_index]
    progress = int((st.session_state.q_index / len(questions)) * 100)  # Cast to int
    st.progress(progress)
    st.write(f"Step {st.session_state.q_index + 1} of {len(questions)}")
    
    with st.form(key=f"form_{st.session_state.q_index}"):
        st.write(f"**{q}**")
        st.caption(hint)
        if st.session_state.q_index == 2:  # Phone number question
            code = st.selectbox("Country Code", list(dial_codes.keys()), index=0)
            phone = st.text_input("Phone Number")
            user_input = f"{code} {phone}"
            if code not in dial_codes:
                st.warning("Sorry, not available in this country. Email us at careerupskillers@gmail.com.")
        else:
            user_input = st.text_input("Your answer")

        if st.form_submit_button("Next") and user_input:
            st.session_state.answers[keys[st.session_state.q_index]] = user_input
            st.session_state.q_index += 1
            if st.session_state.q_index >= len(questions):
                st.session_state.completed = True
