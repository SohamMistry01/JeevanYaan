import os
import pandas as pd
from catboost import CatBoostClassifier
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from django.conf import settings
from .logger import log_response_metadata

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def consistency(response):
    return len(set(response)) / len(response)

# Global model variable to ensure we load it only once
_model = None

def load_model():
    global _model
    if _model is None:
        try:
            _model = CatBoostClassifier()

            model_path = os.path.join(
                settings.BASE_DIR,
                "ml_models",
                "catboost_model_v4.cbm"
            )

            print("Resolved model path:", model_path)
            print("Model exists:", os.path.exists(model_path))

            if os.path.exists(model_path):
                _model.load_model(model_path)
            else:
                print(f"Error: Model file not found at {model_path}")
                return None

        except Exception as e:
            print(f"Error loading model: {e}")
            return None

    return _model

def get_mental_health_analysis(data):
    """
    data: dict containing user inputs (Age, Gender, etc.)
    Returns: dict with prediction_label, probability, and ai_review
    """
    model = load_model()
    if not model:
        return {"error": "Model could not be loaded. Please check server logs."}

    # 1. Prepare Data
    input_df = pd.DataFrame([data])
    
    # Ensure categorical features are of 'category' dtype (matching Streamlit app)
    cat_features = ['Gender', 'Occupation', 'Country', 'Diet_Quality',
                    'Smoking_Habit', 'Alcohol_Consumption', 'Stress_Level']
    
    for col in cat_features:
        if col in input_df.columns:
            input_df[col] = input_df[col].astype('category')

    # 2. Prediction
    try:
        prediction = model.predict(input_df)
        prediction_proba = model.predict_proba(input_df)
        
        is_high_risk = (prediction[0] == 1)
        prediction_label = "High Likelihood" if is_high_risk else "Low Likelihood"
        # Probability of class 1 (High Likelihood)
        high_likelihood_prob = prediction_proba[0][1] 
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

    # 3. AI Review (LangChain)
    ai_review = "AI Review unavailable."
    if groq_api_key:
        try:
            llm = ChatGroq(temperature=0.7, model_name="llama-3.1-8b-instant", api_key=groq_api_key)
            
            expert_prompt = ChatPromptTemplate.from_messages([
                ("system", """
                You are a compassionate and insightful mental health expert. Your role is to analyze user-provided lifestyle data and a machine learning model's prediction about their mental health.
                
                Based on the data provided, offer a supportive and constructive review. Your feedback should:
                1. Gently interpret the model's prediction without being alarmist.
                2. Connect specific user inputs (like work hours, sleep, social media usage) to general well-being principles.
                3. Provide actionable, general advice for improving mental wellness.
                4. Conclude with a strong disclaimer that you are an AI assistant, not a medical professional.
                5. Use a warm, encouraging tone and markdown formatting.
                """),
                ("human", """
                Here is the user's data and the model's prediction.
                
                **User's Lifestyle & Demographic Information:**
                {user_data}
                
                **Machine Learning Model's Prediction:**
                - **Predicted Outcome:** {prediction_label}
                - **Confidence Score (Probability of High Likelihood):** {probability:.2%}
                
                Please provide your thoughtful review.
                """)
            ])

            chain = expert_prompt | llm
            response = chain.invoke({
                "user_data": input_df.to_string(index=False),
                "prediction_label": prediction_label,
                "probability": high_likelihood_prob
            })
            # ✅ Log Metadata
            log_response_metadata(response.response_metadata, "Mental Health Analyzer")
            
            ai_review = response.content
            print("[MENTAL HEALTH ANALYZER Consistency Value]: ", consistency(response.content))

        except Exception as e:
            ai_review = f"Could not generate AI review: {e}"

    return {
        "prediction_label": prediction_label,
        "probability": high_likelihood_prob * 100, # Convert to percentage
        "is_high_risk": is_high_risk,
        "ai_review": ai_review
    }