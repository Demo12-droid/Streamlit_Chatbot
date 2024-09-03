import streamlit as st
import requests
import json
import base64
from io import BytesIO
from PIL import Image
import plotly.io as pio
# from chatbot_backend.chat.main import run_code
import pandas as pd
import time
from streamlit_folium import folium_static
from streamlit_float import *

float_init(theme=True, include_unstable_primary=False)

users_db = {
	"user1": {"password": "pass1"},
	"user2": {"password": "pass2"},
	"user3": {"password": "pass3"},
	"user4": {"password": "pass4"},
}

def get_response(user_input,show_plot,toggle_option,username,session_id):
	url = 'https://filly-pumped-sole.ngrok-free.app/chat/chatbot/'
	headers = {'Content-Type': 'application/json'}
	payload = {
		'username': username,
		'question': user_input,
		'table_key': toggle_option,
		'show_plot': show_plot,
		'session_id': session_id
	}

	start_time = time.time()
	response = requests.post(url, headers=headers, data=json.dumps(payload))
	end_time = time.time()
	
	time_taken = end_time - start_time  
	
	if response.status_code == 200:
	       data = response.json().get('data', {})
	       return data.get('sql', 'No SQL query generated'), data.get('text_summary', 'No summary generated'), data.get('plot', 'No plot generated'),data.get('plot_type', 'No plot generated'),time_taken
	else:
		return None, None, None,None, time_taken

def get_history(username,session_id):
	url = 'https://filly-pumped-sole.ngrok-free.app/chat/session_info/'
	headers = {'Content-Type': 'application/json'}
	payload = {
		'username': username,
		'session_id': session_id,
	}

	response = requests.post(url, headers=headers, data=json.dumps(payload))
	
	if response.status_code == 200:
		data = response.json().get('data', {})
		return data.get('data', 'No_recent_session_history')
	else:
		return None

def save_session_id(username,session_id):
	url = 'https://filly-pumped-sole.ngrok-free.app/chat/save_session_id/'
	headers = {'Content-Type': 'application/json'}
	payload = {
		'username': username,
		'session_id': session_id,
	}

	response = requests.post(url, headers=headers, data=json.dumps(payload))
	
	
	if response.status_code == 200:
		return "Sucessful"
	else:
		return "error saving session credentials"
def authenticate(username, password):
	user = users_db.get(username)
	if user and user["password"] == password:
		return True
	return False

# Function to retrieve session IDs
def get_session_ids(username):
	url = 'https://filly-pumped-sole.ngrok-free.app/chat/get_session_ids/'
	headers = {'Content-Type': 'application/json'}
	payload = {
		"username": username,
	}

	response = requests.post(url, headers=headers, data=json.dumps(payload))
	
	if response.status_code == 200:
		data = response.json().get('data', {})
		return data
	else:
		return None

# Function to generate a new session ID
def generate_new_session_id(username):
	new_session_id = str(uuid.uuid4())
	return new_session_id

def logout():
	st.session_state.logged_in = False
	st.session_state.selected_option = None

def display_plot(plot,plot_type):
	if plot_type=='PIL Image':
		plot_data = base64.b64decode(plot_base64)
		plot_image = Image.open(BytesIO(plot_data))
		st.image(plot_image)
	elif plot_type=='Plotly Figure':
		try:
			img = pio.from_json(json_string)
			st.plotly_chart(img)
		except:
			fig_dict = json.loads(plot)
			img=pio.from_json(json.dumps(fig_dict))
			st.plotly_chart(img)
			
	elif plot_type=='Folium Map':
		components.html(plot,height=390,scrolling=True)
	else:
		pass

if 'logged_in' not in st.session_state:
	st.session_state.logged_in = False
if 'username' not in st.session_state:
	st.session_state.username = ""
if 'show_message' not in st.session_state:
	st.session_state.show_message = True
if 'show_message_for_saved_credentials' not in st.session_state:
	st.session_state.show_message_for_saved_credentials = True
if 'session_ids' not in st.session_state:
	st.session_state.session_ids = []
if 'session_history' not in st.session_state:
	st.session_state.session_history = None
if 'session_id' not in st.session_state:
	st.session_state.session_id = None

# UI for login
if not st.session_state.logged_in:
	st.title("Login")
	username = st.text_input("Username")
	password = st.text_input("Password", type="password")
	if st.button("Login"):
		if authenticate(username, password):
			st.session_state.logged_in = True
			st.session_state.username = username
			
			# Fetch session ids and history only once on login
			if not st.session_state.session_ids:
				st.session_state.session_ids = get_session_ids(st.session_state.username)
			if st.session_state.session_ids and not st.session_state.session_history:
				first_session_id = st.session_state.session_ids[0] if st.session_state.session_ids else None
				st.session_state.session_history = get_history(st.session_state.username, first_session_id)

			st.rerun()
				
		else:
			st.error("Invalid username or password")


if st.session_state.logged_in:
	st.title("Chanakya")
	
	# Sidebar
	st.sidebar.title("Options")

	# Retrieve previous session IDs
	session_ids = st.session_state.session_ids
	if session_ids:
		st.sidebar.header("Select Session")
		array = session_ids + ["Create New Session"] 
		session_option = st.sidebar.radio("Pick a session:",array)
		
		if session_option == "Create New Session":
			if st.sidebar.button("Generate New Session ID"):
				
				new_session_id = generate_new_session_id(st.session_state.username)
				st.session_state.session_id = new_session_id
				st.write(f"New Session ID: {new_session_id}")
				st.session_state.session_ids.append(new_session_id)
				message=save_session_id(st.session_state.username,st.session_state.session_id)
				st.write(message)
				
				st.session_state.session_history = get_history(st.session_state.username, st.session_state.session_id)    #get new_session
				
				st.session_state.show_message_for_saved_credentials = False
				st.rerun()
		else:
			if session_option in session_ids:
				st.session_state.session_id = session_option
				st.session_state.session_history = get_history(st.session_state.username, session_option)   #get history
	else:
		if st.session_state.show_message:
			st.write("No previous sessions found. Creating a new session...")
			new_session_id = generate_new_session_id(st.session_state.username)
			st.session_state.session_id = new_session_id
			st.write(f"New Session ID: {new_session_id}")
			message=save_session_id(st.session_state.username,st.session_state.session_id)
			st.write(message)

			st.session_state.session_ids = get_session_ids(st.session_state.username)   #get session_ids
			st.session_state.session_history = get_history(st.session_state.username, st.session_state.session_id)    #get new_session
				
			
			st.session_state.show_message_for_saved_credentials = False
			st.rerun()
			# Hide the message after displaying
			st.session_state.show_message = False


	st.sidebar.header("Database options")
	toggle_option = st.sidebar.selectbox('Choose a Database:',['congestion', 'toll_plaza_data'])
	
	st.sidebar.header("Display Options")
	show_plot = st.sidebar.checkbox("Plot",value=True)
    
	if st.sidebar.button("Logout"):
		logout()
		st.rerun()
	user_input = st.chat_input("Ask a question...")

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

	st.session_state.messages = st.session_state.session_history


	if 'messages' not in st.session_state:
		st.session_state.messages = []

	if user_input:
		st.session_state.messages.append({"role": "user", "content": user_input})
		sql, text_summary, plot,plot_type, time_taken = get_response(user_input,show_plot,toggle_option,st.session_state.username,st.session_state.session_id)
		
		st.session_state.messages.append({
		    "role": "assistant",
		    "content": {
			"sql": sql,
			"text_summary": text_summary,
			"plot": plot,
			"plot_type":plot_type,
			"time_taken": time_taken
		    }
		})

	if st.session_state.messages:
		for entry in st.session_state.messages:
			role = entry.get('role', 'unknown role')
			content = entry.get('content', {})
			if role =='user':
				with st.chat_message("User"):
					st.write(content)
			elif role == 'assistant':
				sql_query = content.get('sql', None)
				text_summary = content.get('text_summary', None)
				plot = content.get('plot', None)
				plot_type= content.get('plot_type',None)
				time_taken = content.get('time_taken')
	    
				with st.chat_message("assistant"):
					if text_summary:
						if text_summary != "The data queried is too large to summarize":
							st.write(text_summary)
					if plot:
						display_plot(plot,plot_type)
				if time_taken:
					st.write(f"<b>Time taken: {time_taken:.4f} seconds</b>", unsafe_allow_html=True)
