# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
import uuid

# Add the project root directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

from tasks.query import answer_question, get_available_controllers
from tasks.adx_text_to_sql import TextToSQL

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Ensure the required directories exist
os.makedirs(os.path.join(current_dir, 'prompts'), exist_ok=True)
os.makedirs(os.path.join(current_dir, 'reports'), exist_ok=True)

# Initialize TextToSQL instance
text_to_sql = TextToSQL()

@app.route('/')
def home():
    controllers = get_available_controllers()
    return render_template('index.html', controllers=controllers)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    question = data.get('question')
    user_id = data.get('user_id', str(uuid.uuid4()))
    session_id = data.get('session_id', str(uuid.uuid4()))
    controller_id = data.get('controller_id')
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        response = answer_question(
            question, 
            user_id=user_id, 
            session_id=session_id,
            controller_id=controller_id
        )
        return jsonify({
            "answer": response,
            "user_id": user_id,
            "session_id": session_id,
            "controller_id": controller_id
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/adx')
def adx_page():
    return render_template('adx.html')

@app.route('/api/schema')
def get_schema():
    try:
        schema = text_to_sql.get_schema()
        return jsonify(schema)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-sql', methods=['POST'])
def generate_sql():
    try:
        query = request.form.get('query')
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        sql = text_to_sql.generate_sql(query)
        return jsonify({'sql': sql})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-sql', methods=['POST'])
def execute_sql():
    try:
        sql = request.form.get('sql')
        if not sql:
            return jsonify({'error': 'No SQL query provided'}), 400
        
        results = text_to_sql.execute_sql(sql)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.chdir(current_dir)
    app.run(host='0.0.0.0', port=5000)