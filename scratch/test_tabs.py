import streamlit as st

if "page" not in st.session_state:
    st.session_state.page = "main"

tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

with tab1:
    st.write("Tab 1")

with tab2:
    if st.session_state.page == "main":
        def go_next():
            st.session_state.page = "next"
        
        st.button("Go with callback", on_click=go_next)
        
        if st.button("Go without callback"):
            st.session_state.page = "next"
            st.rerun()
    else:
        st.write("Next Page!")
        
        def go_back():
            st.session_state.page = "main"
            
        st.button("Back with callback", on_click=go_back)
        
        if st.button("Back without callback"):
            st.session_state.page = "main"
            st.rerun()
