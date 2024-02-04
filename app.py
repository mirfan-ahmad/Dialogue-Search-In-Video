import streamlit as st
from search_video import search_video


def display_video(uploaded_file, selected_button):
    if selected_button:
        st.write(f"{dialogue} {selected_button}")
        start_time_str = selected_button.split()[-1]
        start_time_int = int(start_time_str) - 1
        st.video(uploaded_file, start_time=start_time_int)


if __name__ == '__main__':
    st.title("Video Dialogue Analyzer")
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4"])

    if uploaded_file is not None:
        dialogue = st.text_input('Enter dialogue to search in video...').lower()
        if st.button('Transcribe'):
            selected_button = search_video(uploaded_file, dialogue)
            display_video(uploaded_file, selected_button)
