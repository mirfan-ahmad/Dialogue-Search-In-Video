import speech_recognition as sr
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor
from tempfile import NamedTemporaryFile
import streamlit as st
from tqdm import tqdm


def extract_audio(video):
    video = AudioSegment.from_file(video, format="mp4")
    audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio.export("audio.wav", format="wav")
    return audio


def transcribe(segment):
    r = sr.Recognizer()
    with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
        temp_wav_path = temp_wav.name
        segment.export(temp_wav_path, format="wav")

    with sr.AudioFile(temp_wav_path) as source:
        audio_text = r.record(source)

    try:
        text = r.recognize_google(audio_text, language='en-US')
        return text
    except sr.RequestError as e:
        st.error(f"Speech recognition request failed. Connection Error!")
    except sr.UnknownValueError:
        st.warning("Google Speech Recognition could not understand audio.")


@st.cache_data(experimental_allow_widgets=True)
def search_video(uploaded_file, dialogue):
    with st.spinner('Processing...'):
        audio = extract_audio(uploaded_file)
        text = []

        with ThreadPoolExecutor() as executor:
            audio_length = len(audio)
            futures = []
            for start_time in tqdm(range(0, audio_length, 1000)):
                end_time = start_time + 1000
                segment = audio[start_time:end_time]

                with NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
                    temp_wav_path = temp_wav.name
                    segment.export(temp_wav_path, format="wav")

                futures.append(executor.submit(transcribe, segment))

            try:
                text, timestamp, transcription = [], [], []
                for idx, item in enumerate(futures):
                    item = item.result()
                    if item is not None:
                        n = item.split()
                        transcription += [i for i in n]
                        timestamp += [idx + i + 1 for i in range(len(n))]
                    try:
                        text += [i for i in item.split()]
                    except:
                        text.append(item)
            except Exception as e:
                st.error(f"Error in transcribing: {e}")

        st.success('Transcribed!')
        st.write('Transcribed Text...')
        st.info(' '.join(transcription))

        dialogue_list = dialogue.rstrip().split(' ')
        length = len(dialogue_list)

        dialogues_dict = {}
        idx = 0
        for i, _ in enumerate(tqdm(transcription)):
            if timestamp[i] not in dialogues_dict:
                dialogues_dict[timestamp[i]] = transcription[i:i + length]

        keys = list(dialogues_dict.keys())
        buttons = []

        for idx, value in enumerate(dialogues_dict.values()):
            matched_items = [item for item in dialogue_list if item in value]
            if len(matched_items) == length:
                buttons.append(f'{dialogue}: {keys[idx]-1}')

        selected_button = st.radio("Select a button", buttons)
        return selected_button