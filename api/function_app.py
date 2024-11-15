import azure.functions as func
import logging
import json
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

app = func.FunctionApp()

@app.route(route="get_advice", auth_level=func.AuthLevel.ANONYMOUS)
def get_advice(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
        user_message = req_body.get('query')
        
        if not user_message:
            return func.HttpResponse(
                json.dumps({
                    'success': False,
                    'advice': 'Please provide a message.'
                }),
                mimetype="application/json",
                status_code=400
            )

        prompt = f"""As a mental health assistant, provide a helpful response to: "{user_message}"
        Be empathetic, supportive, and concise."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        return func.HttpResponse(
            json.dumps({
                'success': True,
                'advice': response_text
            }),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in get_advice: {str(e)}")
        return func.HttpResponse(
            json.dumps({
                'success': False,
                'advice': 'I apologize, but I encountered an error. Please try again.'
            }),
            mimetype="application/json",
            status_code=500
        ) 