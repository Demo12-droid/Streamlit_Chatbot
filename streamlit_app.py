import streamlit as st
import requests
import json
import base64
from io import BytesIO
from PIL import Image
# from chatbot_backend.chat.main import run_code
import pandas as pd
import time

from streamlit_float import *

# Initialize float layout
float_init(theme=True, include_unstable_primary=False)


# Function to get a response from the Django backend
def get_response(user_input,show_plot,toggle_option):
    url = 'http://molly-grateful-hippo.ngrok-free.app/chat/chatbot/'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'username': 'example_user',
        'mode': 'ASK',
        'question': user_input,
        'table_key': toggle_option,
        'show_plot': show_plot,
    }

    MESSAGE="RESPONSE"
    start_time = time.time()
    #response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = time.time()

    time_taken = end_time - start_time  # Calculate time taken
    
    #if response.status_code == 200:
    #    data = response.json().get('data', {})
    #    return data.get('sql', 'No SQL query generated'), data.get('df', 'No data frame generated'), data.get('text_summary', 'No summary generated'), data.get('plot', 'No plot generated'),time_taken
    #else:
    #    return None, None, None, None, None
    return MESSAGE,MESSAGE,MESSAGE,MESSAGE,time_taken



def display_plot(plot_base64):
    if plot_base64:
        plot_data = base64.b64decode(plot_base64)
        plot_image = Image.open(BytesIO(plot_data))
        st.image(plot_image)

# Streamlit app
st.title("Chatbot")

if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

# Custom CSS to fix the position of the input box and send button at the bottom
st.markdown("""
    <style>
    .chat-input-container {
        position: fixed;
        bottom: 20px;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: white;
        padding: 10px 0;
    }
    .chat-input-container > div {
        flex: 1;
    }
    .chat-input-container button {
        margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Chat input and button in a fixed container at the bottom
with st.form(key='chat_form', clear_on_submit=True):
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    user_input_col, button_col = st.columns([4, 1])
    with user_input_col:
        user_input = st.text_input("You: ", key='user_input')
    with button_col:
        submit_button = st.form_submit_button(label='Send')
    st.markdown('</div>', unsafe_allow_html=True)

toggle_option = st.radio("Select a database:", ('congestion', 'toll_plaza_data'))
show_plot = st.checkbox("Plot", value=True)

if submit_button and user_input:
    sql, df, text_summary, plot, time_taken = get_response(user_input,show_plot,toggle_option)
    df = df.to_dict(orient='records') if isinstance(df, pd.DataFrame) else df

    print("sql   ",sql,"\ndf   ",df,"\n summary   ",text_summary,"\n plot    ",plot)
    st.session_state.conversation.append({
        "user_input": user_input,
        "sql": sql,
        "df": df,
        "text_summary": text_summary,
        "plot": plot,
        "time_taken": time_taken 
    })
    
    st.write(f"<b style='color:blue;'>Time taken</b>: {time_taken:.4f} seconds")

for entry in st.session_state.conversation:
    st.markdown(f"<b style='color:blue;'>You: {entry['user_input']}</b> ", unsafe_allow_html=True)
    if entry['sql']:
        st.write(f"SQL Query:\n {entry['sql']}")
    if entry['df']:
        st.write("Data Frame:")
        #st.dataframe(entry['df'])  # Display the DataFrame using st.dataframe
    if entry['text_summary']:
        st.write(f"Summary:\n{entry['text_summary']}")
    if entry['plot']:
        st.write("Plot:")
        #display_plot(entry['plot'])  # Display the plot
