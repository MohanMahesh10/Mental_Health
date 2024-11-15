from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_advice', methods=['POST'])
def get_advice():
    try:
        user_message = request.json.get('query', '')
        print(f"Received message: {user_message}")  # Debug print
        
        if not user_message:
            return jsonify({
                'success': False,
                'advice': 'Please provide a message.'
            })

        prompt = f"""As a mental health assistant, provide a helpful response to: "{user_message}"
        Be empathetic, supportive, and concise."""
        
        print(f"Sending prompt to Gemini: {prompt}")  # Debug print
        
        try:
            response = model.generate_content(prompt)
            print(f"Gemini response: {response}")  # Debug print
            response_text = response.text.strip()
            print(f"Processed response: {response_text}")  # Debug print
            
            return jsonify({
                'success': True,
                'advice': response_text
            })
        except Exception as api_error:
            print(f"Gemini API error: {str(api_error)}")  # Debug print
            raise api_error

    except Exception as e:
        print(f"Error in get_advice: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'advice': 'I apologize, but I encountered an error. Please try again.'
        })

if __name__ == '__main__':
    # Update the host and port configuration
    port = os.getenv('PORT', 5000)
    app.run(host='0.0.0.0', port=int(port)) 