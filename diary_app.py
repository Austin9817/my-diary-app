import streamlit as st

st.title("My First Diary App 🎉")
st.write("Hello! It works!")

name = st.text_input("What's your name?")
st.write(f"Nice to meet you, {name}")
