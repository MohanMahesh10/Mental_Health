import logging
import json
import azure.functions as func
import google.generativeai as genai
import os
from dotenv import load_dotenv

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Enable CORS
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    try:
        # Handle OPTIONS request for CORS
        if req.method.lower() == "options":
            return func.HttpResponse(status_code=200, headers=headers)

        # Load environment variables
        load_dotenv()

        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Get request body
        try:
            req_body = req.get_json()
            user_message = req_body.get('query')
        except ValueError:
            return func.HttpResponse(
                body=json.dumps({
                    'success': False,
                    'advice': 'Invalid JSON in request body'
                }),
                headers=headers,
                status_code=400
            )
        
        if not user_message:
            return func.HttpResponse(
                body=json.dumps({
                    'success': False,
                    'advice': 'Please provide a message.'
                }),
                headers=headers,
                status_code=400
            )

        prompt = f"""As a mental health assistant, provide a helpful response to: "{user_message}"
        Be empathetic, supportive, and concise."""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        return func.HttpResponse(
            body=json.dumps({
                'success': True,
                'advice': response_text
            }),
            headers=headers
        )
        
    except ValueError as ve:
        logging.error(f"Value Error: {str(ve)}")
        return func.HttpResponse(
            body=json.dumps({
                'success': False,
                'advice': 'Configuration error: API key not set'
            }),
            headers=headers,
            status_code=500
        )
    except Exception as e:
        logging.error(f"Error in get_advice: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({
                'success': False,
                'advice': 'I apologize, but I encountered an error. Please try again.'
            }),
            headers=headers,
            status_code=500
        ) 