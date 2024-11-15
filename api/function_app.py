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
            logging.info("Handling OPTIONS request")
            return func.HttpResponse(status_code=200, headers=headers)

        # Load environment variables
        load_dotenv()

        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        logging.info("API Key present: %s", "Yes" if api_key else "No")
        
        if not api_key:
            logging.error("GEMINI_API_KEY not found in environment variables")
            return func.HttpResponse(
                body=json.dumps({
                    'success': False,
                    'advice': 'API key not configured. Please contact support.'
                }),
                headers=headers,
                status_code=500
            )

        # Initialize Gemini
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            logging.info("Gemini model initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing Gemini: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({
                    'success': False,
                    'advice': 'Error initializing AI model'
                }),
                headers=headers,
                status_code=500
            )

        # Get request body
        try:
            req_body = req.get_json()
            user_message = req_body.get('query')
            logging.info(f"Received message: {user_message}")
        except ValueError as e:
            logging.error(f"Error parsing request body: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({
                    'success': False,
                    'advice': 'Invalid request format'
                }),
                headers=headers,
                status_code=400
            )
        
        if not user_message:
            logging.warning("Empty message received")
            return func.HttpResponse(
                body=json.dumps({
                    'success': False,
                    'advice': 'Please provide a message.'
                }),
                headers=headers,
                status_code=400
            )

        # Generate response
        try:
            prompt = f"""As a mental health assistant, provide a helpful response to: "{user_message}"
            Be empathetic, supportive, and concise."""
            
            logging.info("Sending prompt to Gemini")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            logging.info(f"Received response from Gemini: {response_text[:100]}...")
            
            return func.HttpResponse(
                body=json.dumps({
                    'success': True,
                    'advice': response_text
                }),
                headers=headers
            )
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            return func.HttpResponse(
                body=json.dumps({
                    'success': False,
                    'advice': 'Error generating response'
                }),
                headers=headers,
                status_code=500
            )
        
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return func.HttpResponse(
            body=json.dumps({
                'success': False,
                'advice': 'An unexpected error occurred'
            }),
            headers=headers,
            status_code=500
        ) 