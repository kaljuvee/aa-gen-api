import os
import json
import logging
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

class SearchManager:
    def __init__(self):
        self.load_index_metadata()
        self.setup_clients()

    def load_index_metadata(self):
        metadata_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'config', 
            'index_metadata_multi.json'
        )
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        self.default_index = self.metadata.get('default_index', 'apc-j140-bin-005c')

    def setup_clients(self):
        self.search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.search_key = os.getenv("AZURE_SEARCH_KEY")
        self.openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_key = os.getenv("AZURE_OPENAI_KEY")
        self.openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

        # Load system prompt
        prompt_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')
        with open(os.path.join(prompt_dir, 'system_prompt.md'), 'r') as f:
            self.system_prompt = f.read().strip()

        self.openai_client = AzureOpenAI(
            api_key=self.openai_key,
            api_version="2023-05-15",
            azure_endpoint=self.openai_endpoint
        )

        self.search_clients = {}
        for controller_id, config in self.metadata.items():
            if controller_id != 'default_index':  # Skip the default_index entry
                self.search_clients[controller_id] = SearchClient(
                    self.search_endpoint, 
                    config['index_name'],  # Use index_name from config
                    AzureKeyCredential(self.search_key)
                )

    def get_search_client(self, controller_id=None):
        if not controller_id:
            return self.search_clients[self.default_index]
        
        if controller_id not in self.metadata or controller_id == 'default_index':
            raise ValueError(f"Controller {controller_id} not supported")
        
        return self.search_clients[controller_id]

    def get_prompt_name(self, controller_id=None):
        if not controller_id:
            return self.metadata[self.default_index]['prompt_name']
        return self.metadata[controller_id]['prompt_name']

# Global instance
search_manager = SearchManager()

def search_documents(query, controller_id=None):
    try:
        search_client = search_manager.get_search_client(controller_id)
        results = search_client.search(query, top=10)
        return [result['content'] for result in results]
    except ValueError as e:
        return [str(e)]

def answer_question(question, user_id=None, session_id=None, controller_id=None):
    relevant_docs = search_documents(question, controller_id)
    
    if len(relevant_docs) == 1 and relevant_docs[0].startswith("Controller"):
        return relevant_docs[0]
    
    if not relevant_docs:
        return "I don't have enough information to answer that question. Could you please provide more specific details?"
    
    context = "\n".join(relevant_docs)
    controller_info = ""
    if controller_id:
        controller_config = search_manager.metadata[controller_id]
        controller_info = f"\nController: {controller_config['name']} ({controller_config['description']})"
    
    user_context = f"\nUser ID: {user_id}\nSession ID: {session_id}" if user_id and session_id else ""

    prompt = f"""
    Context: {context}{controller_info}{user_context}

    Question: {question}

    Answer the question based on the context provided. If the answer is not in the context, ask the user to provide more specific details.
    """

    response = search_manager.openai_client.chat.completions.create(
        model=search_manager.openai_deployment,
        messages=[
            {"role": "system", "content": search_manager.system_prompt},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )

    return response.choices[0].message.content.strip()

def get_available_controllers():
    """Return list of available controllers for UI"""
    return {
        controller_id: config['name'] 
        for controller_id, config in search_manager.metadata.items()
        if controller_id != 'default_index'
    }
