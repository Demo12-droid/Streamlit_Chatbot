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

# Initialize float layout
float_init(theme=True, include_unstable_primary=False)


# Function to get a response from the Django backend
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
    st.write(plot_base64)
    if plot_base64:
        plot_data = base64.b64decode(plot_base64)
        plot_image = Image.open(BytesIO(plot_data))
        st.image(plot_image)
            

# Streamlit app
st.title("Chanakya")

if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []


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

if user_input:
    sql, df, text_summary, plot, time_taken = get_response(user_input,show_plot,toggle_option)

    # st.write("sql",sql,"\n\ndf",df,"\n\ntext_summary",text_summary)
    # df = df.to_dict(orient='records') if isinstance(df, pd.DataFrame) else df
    st.session_state.conversation.append({
        "user_input": user_input,
        "sql": sql,
        "df": df,
        "text_summary": text_summary,
        "plot": plot,
        "time_taken": time_taken 
    })

for entry in st.session_state.conversation:
    # st.markdown(f"<b style='color:#0B51A0;'>You: {entry['user_input']}</b> ", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="text-align: right; margin-right: 10px;">
            <span style="background-color: #f1f1f1; border-radius: 5px; padding: 10px; display: inline-block;">
                <b style="color:#0B51A0;">{entry['user_input']}</b>
            </span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    # if entry['sql']:
    #     st.write(f"SQL Query:\n {entry['sql']}")
    # if entry['df']:
    #     st.write("Data:")
    #     st.dataframe(entry['df'])  # Display the DataFrame using st.dataframe
    # if entry['text_summary']:
    #     st.write(f"Summary:\n {entry['text_summary']}")
    # if entry['plot']:
    #     st.write("Plot:")
    #     display_plot(entry['plot'])  # Display the plot
    if entry['df']:
        st.markdown(
            """
            <div style="margin: 10px 0;">
                <span style="background-color: #f1f1f1; border-radius: 5px; padding: 10px; display: inline-block;">
                    <b>Data:</b>
                </span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.dataframe(entry['df'])  # Display the DataFrame using st.dataframe
    
    if entry['text_summary']:
        st.markdown(
            f"""
            <div style="margin: 10px 0;">
                <span style="background-color: #f1f1f1; border-radius: 5px; padding: 10px; display: inline-block;">
                    <b>Summary: </b><p>{entry['text_summary']}</p>
                </span>
            </div>
            """,
            # <div style="background-color: #f1f1f1; border-radius: 5px; padding: 10px;">
            # </div>
            # style="color:#0B51A0;"
            # """, 
            unsafe_allow_html=True
        )
    
    if entry['plot']:
        st.markdown(
            """
            <div style="margin: 10px 0;">
                <span style="background-color: #f1f1f1; border-radius: 5px; padding: 10px; display: inline-block;">
                    <b>Plot:</b>
                </span>
            </div>
            """, 
            unsafe_allow_html=True
        )
        # st.write(type(entry['plot']))
        try:
            display_plot(entry['plot'])

        except:
            components.html(entry['plot'],scrolling=True)

    if entry['sql'] is not None and entry['df'] is None:
        st.markdown("<b>No data is available for the given question.If data is available, please retry</b>", unsafe_allow_html=True)
    # st.markdown(f"<b>Time taken: {entry['time_taken']:.4f} seconds</b>", unsafe_allow_html=True)
