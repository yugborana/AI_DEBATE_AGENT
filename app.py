import streamlit as st
import uuid
import sqlite3
import time

# Import the compiled graph function from your AI Debater backend
from debate.graph import get_compiled_graph

# --- Configuration ---
DEBATE_DB = "memory.db"

# Get the compiled graph application
# This is the "chatbot"
try:
    chatbot = get_compiled_graph()
    st.session_state['backend_loaded'] = True
except ImportError as e:
    st.error(f"Failed to import backend: {e}. Make sure the 'debate' package is in your PYTHONPATH.")
    st.stop()
except Exception as e:
    st.error(f"Failed to load compiled graph: {e}")
    st.stop()


# **************************************** Utility Functions *************************

def retrieve_all_threads():
    """
    Manually query the SqliteSaver database for all thread IDs.
    This version correctly checks for the 'threads' table.
    """
    threads = []
    try:
        conn = sqlite3.connect(database=DEBATE_DB, check_same_thread=False)
        cursor = conn.cursor()

        # Check if LangGraph thread table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='threads'"
        )
        if cursor.fetchone():
            # The 'threads' table stores metadata about each thread
            cursor.execute("SELECT DISTINCT thread_id FROM threads ORDER BY thread_ts DESC")
            threads = [row[0] for row in cursor.fetchall()]
        
        # We don't need a fallback, as 'threads' is the correct table
        # used by SqliteSaver.

        conn.close()
    except sqlite3.OperationalError:
        # DB or table might not exist on first run
        pass
    except Exception as e:
        # Use st.warning to show the error in the app if something goes wrong
        st.warning(f"Error retrieving threads: {e}")

    return threads

def generate_thread_id():
    """Generates a new string UUID."""
    return str(uuid.uuid4())

def reset_chat():
    """Resets the chat to a new, empty thread."""
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    # Add new thread to the top of the list
    if 'chat_threads' in st.session_state:
        st.session_state['chat_threads'].insert(0, thread_id)
    else:
        st.session_state['chat_threads'] = [thread_id]
    st.session_state['message_history'] = []

def add_thread(thread_id):
    """Adds a thread to the session state list if not already present."""
    if 'chat_threads' not in st.session_state:
        st.session_state['chat_threads'] = []
        
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].insert(0, thread_id)

def load_conversation(thread_id):
    """
    Loads a "conversation" (a completed debate) from the graph's state.
    A debate is reconstructed as a 2-turn conversation:
    1. User: The topic
    2. Assistant: The final markdown summary
    """
    try:
        state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        temp_messages = []
        
        if state:
            topic = state.values.get('topic')
            final_markdown = state.values.get('final_markdown')
            
            if topic:
                temp_messages.append({'role': 'user', 'content': topic})
            if final_markdown:
                temp_messages.append({'role': 'assistant', 'content': final_markdown})
        
        return temp_messages
    except Exception as e:
        st.error(f"Error loading thread state: {e}")
        return []

# **************************************** Session Setup ******************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()
    # Ensure the default new thread is in the list
    if not st.session_state['chat_threads']:
        add_thread(st.session_state['thread_id'])

# Make sure the current thread is in the list
add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************

st.sidebar.title('AI Debater 🤖')
st.sidebar.markdown("---")

if st.sidebar.button('New Debate', use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.header('My Debates')

# Display threads
for thread_id in st.session_state['chat_threads']:
    try:
        # Get the state to find the topic for a better button label
        state_for_summary = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        button_label = f"Debate: {thread_id[:8]}..." # Default label
        
        if state_for_summary:
            topic = state_for_summary.values.get('topic')
            if topic:
                button_label = topic[:40] + "..." if len(topic) > 40 else topic
        
        if st.sidebar.button(button_label, key=thread_id, use_container_width=True):
            st.session_state['thread_id'] = thread_id
            st.session_state['message_history'] = load_conversation(thread_id)
            st.rerun()
            
    except Exception as e:
        # Handle cases where a thread might be corrupted or inaccessible
        st.sidebar.text(f"Error loading {thread_id[:8]}")


# **************************************** Main UI ************************************

st.header("AI Debater")
st.write("Enter a topic to start a debate. The AI will generate two opposing stances, write arguments for both, rebut them, and declare a winner.")

# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        # Use st.markdown for the assistant's response, as it's the final_markdown
        if message['role'] == 'assistant':
            st.markdown(message['content'])
        else:
            st.text(message['content']) # Keep user input as plain text

user_input = st.chat_input('Enter a debate topic...')

if user_input:
    # Check if a debate has already run in this thread
    if st.session_state['message_history']:
        st.warning("This debate is already complete. Click 'New Debate' in the sidebar to start another.", icon="⚠️")
    else:
        # Start a new debate
        st.session_state['message_history'].append({'role': 'user', 'content': user_input})
        with st.chat_message('user'):
            st.text(user_input)

        # Run the debate graph
        with st.chat_message('assistant'):
            CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}
            # We need to pass 'current_round' as required by the rebuttal nodes
            graph_input = {"topic": user_input, "current_round": 0} 

            # This placeholder will be updated with node progress
            stream_placeholder = st.empty()
            stream_placeholder.markdown("Starting debate...")
            
            final_markdown = ""

            try:
                # We use stream_mode="events" (the default) to get node completion events
                # This lets us show progress without token-by-token streaming
                for event in chatbot.stream(graph_input, config=CONFIG):
                    # `event` is a dictionary with one key: the name of the node that just ran
                    for node_name, node_output in event.items():
                        # Display progress
                        stream_placeholder.markdown(f"Running node: **{node_name}**...")
                        
                        # Check if this is the final node
                        if node_name == "assemble":
                            if isinstance(node_output, dict):
                                final_markdown = node_output.get("final_markdown", "")
                
                # After the loop, the stream is done.
                if final_markdown:
                    # Update the placeholder with the final, complete markdown
                    stream_placeholder.markdown(final_markdown) 
                    st.session_state['message_history'].append(
                        {'role': 'assistant', 'content': final_markdown}
                    )
                    # Make sure this new thread is in the list
                    add_thread(st.session_state['thread_id'])
                else:
                    # Something went wrong, try to get state
                    final_state = chatbot.get_state(CONFIG)
                    final_markdown = final_state.values.get('final_markdown')
                    if final_markdown:
                        stream_placeholder.markdown(final_markdown)
                        st.session_state['message_history'].append(
                            {'role': 'assistant', 'content': final_markdown}
                        )
                        add_thread(st.session_state['thread_id'])
                    else:
                        st.error("Error: Could not retrieve final debate summary.")
                        st.session_state['message_history'].pop() # Remove the user message
            
            except Exception as e:
                st.error(f"An error occurred during the debate: {e}")
                # Remove the user message if the process failed
                if st.session_state['message_history'][-1]['role'] == 'user':
                    st.session_state['message_history'].pop()