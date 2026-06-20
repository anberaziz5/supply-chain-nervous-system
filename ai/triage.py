import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def generate_mitigation_strategy(shipment_id, origin, destination, risk_score, weather, congestion):
    prompt = f"""
    You are an elite Supply Chain Systems Architect. 
    A critical shipment ({shipment_id}) moving from {origin} to {destination} has been flagged by our ML models with a {risk_score}% probability of severe delay.
    
    Telemetry Data:
    - Current Weather: {weather}
    - Port Congestion Index: {congestion}/1.0
    
    Draft a concise, highly technical operational mitigation directive. 
    Provide 3 immediate actions to reroute, expedite, or buffer the inventory to prevent a bullwhip effect across the network.
    Do not use generic corporate jargon. Be specific and tactical.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Triage Error: {str(e)}"