import streamlit as st
import os
from strands import Agent
from strands.models import BedrockModel
from strands_tools import use_llm, memory, mem0_memory

# Import the specialized assistants
from multi_agent_example.computer_science_assistant import computer_science_assistant
from multi_agent_example.english_assistant import english_assistant
from multi_agent_example.language_assistant import language_assistant
from multi_agent_example.math_assistant import math_assistant
from multi_agent_example.no_expertise import general_assistant

# Constants
USER_ID = "mem0_user"

# Check if OpenSearch is available
OPENSEARCH_AVAILABLE = bool(os.environ.get("OPENSEARCH_HOST"))

# Memory system prompt
MEMORY_SYSTEM_PROMPT = f"""You are a personal assistant that maintains context by remembering user details.

Capabilities:
- Store new information using mem0_memory tool (action="store")
- Retrieve relevant memories (action="retrieve")
- List all memories (action="list")
- Provide personalized responses

Key Rules:
- Always include user_id={USER_ID} in tool calls
- Be conversational and natural in responses
- Format output clearly
- Acknowledge stored information
- Only share relevant information
- Politely indicate when information is unavailable
"""

def determine_action(agent, query):
    """Determine if the query should go to teacher or knowledge base."""
    result = agent.tool.use_llm(
        prompt=f"Query: {query}",
        system_prompt=ACTION_SYSTEM_PROMPT
    )
    
    action_text = str(result).lower().strip()
    
    if "teacher" in action_text:
        return "teacher"
    else:
        return "knowledge_base"

def determine_kb_action(agent, query):
    """Determine if the query is a store or retrieve action."""
    result = agent.tool.use_llm(
        prompt=f"Query: {query}",
        system_prompt=KB_ACTION_SYSTEM_PROMPT
    )
    
    action_text = str(result).lower().strip()
    
    if "store" in action_text:
        return "store"
    else:
        return "retrieve"

def run_memory_agent(query):
    """Process a user query with the memory agent."""
    agent = Agent(
        system_prompt=MEMORY_SYSTEM_PROMPT,
        tools=[mem0_memory, use_llm],
    )
    
    response = agent(query)
    return str(response)

def run_kb_agent(query):
    """Process a user query with the knowledge base agent."""
    agent = Agent(tools=[memory, use_llm])
    
    action = determine_kb_action(agent, query)
    
    if action == "store":
        agent.tool.memory(action="store", content=query)
        return "I've stored this information."
    else:
        result = agent.tool.memory(
            action="retrieve", 
            query=query,
            min_score=0.4,
            max_results=9
        )
        result_str = str(result)
        
        answer = agent.tool.use_llm(
            prompt=f"User question: \"{query}\"\n\nInformation from knowledge base:\n{result_str}\n\nProvide a helpful answer:",
            system_prompt=KB_ANSWER_SYSTEM_PROMPT
        )
        return str(answer)

# Define the teacher's assistant system prompt
ACTION_SYSTEM_PROMPT = """
You are a routing assistant that determines whether a query should go to:
1. TEACHER - for educational questions (math, english, language, computer science, general knowledge)
2. KNOWLEDGE_BASE - for storing/retrieving personal information

Reply with EXACTLY ONE WORD - either "teacher" or "knowledge_base".

Examples:
- "What is 2+2?" -> "teacher"
- "Help me write an essay" -> "teacher"
- "Translate hello to Spanish" -> "teacher"
- "Remember my birthday is July 4" -> "knowledge_base"
- "What's my birthday?" -> "knowledge_base"
- "My name is John" -> "knowledge_base"
"""

KB_ACTION_SYSTEM_PROMPT = """
You are a knowledge base assistant focusing ONLY on classifying user queries.
Reply with EXACTLY ONE WORD - either "store" or "retrieve".

Examples:
- "Remember that my birthday is July 4" -> "store"
- "What's my birthday?" -> "retrieve"
- "My name is John" -> "store"
- "Who am I?" -> "retrieve"
"""

KB_ANSWER_SYSTEM_PROMPT = """
You are a helpful knowledge assistant that provides clear, concise answers 
based on information retrieved from a knowledge base. Be direct and conversational.
"""
TEACHER_SYSTEM_PROMPT = """
You are TeachAssist, a sophisticated educational orchestrator designed to coordinate educational support across multiple subjects. Your role is to:

1. Analyze incoming student queries and determine the most appropriate specialized agent to handle them:
   - Math Agent: For mathematical calculations, problems, and concepts
   - English Agent: For writing, grammar, literature, and composition
   - Language Agent: For translation and language-related queries
   - Computer Science Agent: For programming, algorithms, data structures, and code execution
   - General Assistant: For all other topics outside these specialized domains

2. Key Responsibilities:
   - Accurately classify student queries by subject area
   - Route requests to the appropriate specialized agent
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents are needed

3. Decision Protocol:
   - If query involves calculations/numbers → Math Agent
   - If query involves writing/literature/grammar → English Agent
   - If query involves translation → Language Agent
   - If query involves programming/coding/algorithms/computer science → Computer Science Agent
   - If query is outside these specialized areas → General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
"""

# Set up the page
st.set_page_config(page_title="TeachAssist - Educational Assistant", layout="wide")
st.title("TeachAssist - Educational Assistant")
st.write("Ask a question in any subject area, and I'll route it to the appropriate specialist.")

# Backend selection
backend_options = ["Bedrock Knowledge Base"]
if OPENSEARCH_AVAILABLE:
    backend_options.append("Memory Agent (OpenSearch)")

selected_backend = st.selectbox(
    "Select Memory Backend:",
    backend_options,
    help="Choose between Bedrock Knowledge Base or Memory Agent with OpenSearch backend"
)

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize the teacher agent
@st.cache_resource
def get_teacher_agent():
    # Specify the Bedrock ModelID
    bedrock_model = BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",
        temperature=0.3,
    )
    
    # Create the teacher agent with specialized tools
    return Agent(
        model=bedrock_model,
        system_prompt=TEACHER_SYSTEM_PROMPT,
        callback_handler=None,
        tools=[math_assistant, language_assistant, english_assistant, computer_science_assistant, general_assistant],
    )

# Get user input
query = st.chat_input("Ask your question here...")

if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Create routing agent
            routing_agent = Agent(tools=[use_llm])
            
            # Determine where to route the query
            route = determine_action(routing_agent, query)
            
            with st.spinner("Processing..."):
                if route == "teacher":
                    # Get the teacher agent and process educational queries
                    teacher_agent = get_teacher_agent()
                    response = teacher_agent(query)
                    content = str(response)
                else:
                    # Process knowledge base or memory queries based on selected backend
                    if selected_backend == "Memory Agent (OpenSearch)":
                        content = run_memory_agent(query)
                    else:
                        content = run_kb_agent(query)
            
            # Display the response
            message_placeholder.markdown(content)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": content})
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})