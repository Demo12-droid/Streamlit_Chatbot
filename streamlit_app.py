import streamlit as st
import requests
import json
import base64
from io import BytesIO
from PIL import Image
# from chatbot_backend.chat.main import run_code
import pandas as pd
import time

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

    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = time.time()

    time_taken = end_time - start_time  # Calculate time taken
    
    if response.status_code == 200:
        data = response.json().get('data', {})
        return data.get('sql', 'No SQL query generated'), data.get('df', 'No data frame generated'), data.get('text_summary', 'No summary generated'), data.get('plot', 'No plot generated'),time_taken
    else:
        return None, None, None, None, None
    
def display_plot(plot_base64):
    if plot_base64:
        plot_data = base64.b64decode(plot_base64)
        plot_image = Image.open(BytesIO(plot_data))
        st.image(plot_image)

# Streamlit app
st.title("Chatbot")

if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

with st.form(key='chat_form'):
    user_input = st.text_input("You: ", key='user_input')
    submit_button = st.form_submit_button(label='Send')

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
        st.dataframe(entry['df'])  # Display the DataFrame using st.dataframe
    if entry['text_summary']:
        st.write(f"Summary:\n{entry['text_summary']}")
    if entry['plot']:
        st.write("Plot:")
        display_plot(entry['plot'])  # Display the plot
