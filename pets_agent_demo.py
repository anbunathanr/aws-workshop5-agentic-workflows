#!/usr/bin/env python3
"""
Pets Knowledge Base Agent Demo

This script demonstrates how to create a Strands agent that uses
the pets knowledge base to answer questions about pet care.

Usage:
    python pets_agent_demo.py [knowledge_base_id]
"""

import sys
import boto3
from strands import Agent, tool

@tool
def retrieve_from_knowledge_base(query: str, knowledge_base_id: str = "DGRJWBIGET") -> str:
    """Retrieve information from the pets knowledge base.
    
    Args:
        query: The question or search query about pets
        knowledge_base_id: The Bedrock knowledge base ID
        
    Returns:
        Relevant information from the knowledge base
    """
    try:
        import os
        region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        
        bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
        
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledge_base_id,
                    'modelArn': f'arn:aws:bedrock:{region}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0'
                }
            }
        )
        
        return response['output']['text']
        
    except Exception as e:
        return f"Error retrieving from knowledge base: {str(e)}"

def create_pets_agent(knowledge_base_id):
    """Create a Strands agent with access to the pets knowledge base."""
    
    # System prompt for the pets agent
    system_prompt = f"""You are a helpful pet care assistant with access to a comprehensive knowledge base about pets.

You can help with:
- Pet care and health questions
- Feeding and nutrition advice
- Behavioral guidance
- Breed information
- Veterinary care recommendations
- General pet ownership tips

When answering questions:
1. Use the retrieve_from_knowledge_base tool to find relevant, accurate information
2. Provide clear, practical advice based on the retrieved information
3. Always recommend consulting a veterinarian for serious health concerns
4. Be friendly and supportive to pet owners
5. If you're not sure about something, say so and suggest professional consultation

The knowledge base ID is: {knowledge_base_id}"""

    # Create the agent with the retrieve tool
    agent = Agent(
        system_prompt=system_prompt,
        tools=[retrieve_from_knowledge_base]
    )
    
    return agent

def main():
    """Main function to run the pets agent demo."""
    
    # Use the knowledge base ID from the workshop
    knowledge_base_id = "DGRJWBIGET"
    
    # Allow override from command line argument
    if len(sys.argv) > 1:
        knowledge_base_id = sys.argv[1]
    
    print("=== Pets Knowledge Base Agent Demo ===")
    print(f"Using Knowledge Base ID: {knowledge_base_id}")
    print()
    
    try:
        # Create the pets agent
        agent = create_pets_agent(knowledge_base_id)
        
        print("Pets agent created successfully!")
        print("You can now ask questions about pet care, health, nutrition, and more.")
        print("Type 'exit' to quit.")
        print()
        
        # Interactive loop
        while True:
            try:
                question = input("Ask about pets: ")
                
                if question.lower() in ['exit', 'quit', 'bye']:
                    print("Goodbye! Take good care of your pets! 🐕🐱")
                    break
                
                if not question.strip():
                    continue
                
                print("\nThinking...")
                response = agent(question)
                print(f"\nAnswer: {response}")
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! Take good care of your pets! 🐕🐱")
                break
            except Exception as e:
                print(f"Error: {e}")
                print("Please try asking your question again.")
    
    except Exception as e:
        print(f"Error creating pets agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Check if AWS credentials are configured
    try:
        # Set default region explicitly
        import os
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        # Try to get caller identity to verify credentials work
        session = boto3.Session(region_name='us-east-1')
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS User/Role: {identity['Arn']}")
        print(f"AWS Region: us-east-1")
        print()
    except Exception as e:
        print(f"Error: AWS credentials not configured properly: {e}")
        print("Please configure your AWS credentials using one of these methods:")
        print("1. aws configure")
        print("2. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION")
        print("3. Use IAM roles (if running on EC2)")
        print("\nMake sure AWS_DEFAULT_REGION is set (e.g., us-east-1)")
        sys.exit(1)
    
    main()