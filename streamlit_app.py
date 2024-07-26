import streamlit as st
import requests
import json
import base64
from io import BytesIO
from PIL import Image
# from chatbot_backend.chat.main import run_code
import pandas as pd
import time
from streamlit_folium import folium_static
from streamlit_float import *

float_init(theme=True, include_unstable_primary=False)

def get_response(user_input,show_plot,toggle_option):
    url = 'http://molly-grateful-hippo.ngrok-free.app/chat/chatbot/'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'username': 'test3',
        'mode': 'ASK',
        'question': user_input,
        'table_key': toggle_option,
        'show_plot': show_plot,
        'session_id': 'test'
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = time.time()

    time_taken = end_time - start_time  
    
    if response.status_code == 200:
       data = response.json().get('data', {})
       return data.get('sql', 'No SQL query generated'), data.get('df', 'No data frame generated'), data.get('text_summary', 'No summary generated'), data.get('plot', 'No plot generated'),time_taken
    else:
       return None, None, None, None, time_taken
    
def display_plot(plot_base64):
    try:
        #plot_base64
        plot_data = base64.b64decode(plot_base64)
        plot_image = Image.open(BytesIO(plot_data))
        st.image(plot_image)
    except:
        #indicator type
        img_bytes.seek(0)
        img = Image.open(img_bytes)
        st.image(img)

# Streamlit app
st.title("Chanakya")

user_input = st.chat_input("Ask a question...")

st.sidebar.title("Options")

st.sidebar.header("Database options")
toggle_option = st.sidebar.selectbox(
    'Choose a Database:',
    ['congestion', 'toll_plaza_data']
)

st.sidebar.header("Display Options")
show_plot = st.sidebar.checkbox("Plot",value=True)

if toggle_option == "congestion":
    st.markdown("<b style='color:#0B51A0;'>Try asking the following questions: </b>", unsafe_allow_html=True)
    if st.button("What is the average extent in jan 2024", type="secondary"):
        user_input = "What is the average extent in jan 2024"    
    if st.button("What is the range of the data", type="secondary"):
        user_input="What is the range of the data"
    if st.button("What are the details of the highest extent", type="secondary"):
        user_input="What are the details of the highest extent"
    if st.button("What has higher average extent jan 2024 or feb 2024", type="secondary"):
        user_input="What has higher average extent jan 2024 or feb 2024"
    if st.button("What are the congested locations on the CBD 1 corridor", type="secondary"):
        user_input="What are the congested locations on the CBD 1 corridor"
    if st.button("What locations were congested in february", type="secondary"):
        user_input="What locations were congested in february"
    if st.button("What are the congested locations in the Koramangala 2nd Block area", type="secondary"):
        user_input="What are the congested locations in the Koramangala 2nd Block area"


if toggle_option == "toll_plaza_data":
    st.markdown("<b style=\"color:#0B51A0;\">Try asking the following questions:</b>", unsafe_allow_html=True)
    if st.button("What is the total number of vehicles of type MAV in Jan 2024", type="secondary"):
        user_input="What is the total number of vehicles of type MAV in Jan 2024"
    if st.button("What is the time range of the data?", type="secondary"):
        user_input="What is the time range of the data?"
    if st.button("What is the revenue of different vehicle classes?", type="secondary"):
        user_input="What is the revenue of different vehicle classes?"
    if st.button("What is the revenue from different vehicle classes in Feb 2024", type="secondary"):
        user_input="What is the revenue from different vehicle classes in Feb 2024"
    if st.button("What is the total number of vehicles of each vehicle class in Jan 2024", type="secondary"):
        user_input="What is the total number of vehicles in each vehicle class in Jan 2024"

if 'messages' not in st.session_state:
    st.session_state.messages = []

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    sql, df, text_summary, plot, time_taken = get_response(user_input,show_plot,toggle_option)

    # df = df.to_dict(orient='records') if isinstance(df, pd.DataFrame) else df
    st.session_state.messages.append({
        "role": "assistant",
        "content": {
            "user_input": user_input,
            "sql": sql,
            "df": df,
            "text_summary": text_summary,
            "plot": plot,
            "time_taken": time_taken 
        }
    })

for entry in st.session_state.messages:
    role = entry.get('role', 'unknown role')
    content = entry.get('content', {})

    if role == 'user':
        with st.chat_message("User"):
            st.write(content)
    elif role == 'assistant':
        sql_query = content.get('sql', None)
        text_summary = content.get('text_summary', None)
        plot = content.get('plot', None)
        df = content.get('df', None) 
        time_taken = content.get('time_taken')

        if sql_query is not None and df is None:
            with st.chat_message("assistant"):
                st.write("No data is available for the given question.If data is available, please retry")
        else:            
            with st.chat_message("assistant"):
                if df:
                    st.dataframe(df)
                if text_summary:
                    st.write(text_summary)
                if plot:
                    try:
                        display_plot(plot)
                    except:
                        components.html(plot,height=390,scrolling=True)
                st.write(f"<b>Time taken: {time_taken:.4f} seconds</b>", unsafe_allow_html=True)
