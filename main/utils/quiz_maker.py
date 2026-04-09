import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from main.utils.logger import log_response_metadata

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def consistency(response):
    return len(set(response)) / len(response)

def generate_quiz_data(subject, topic, subtopic, difficulty, num_questions):
    """
    Generates the quiz questions using Groq API.
    Returns a list of questions or None on failure.
    """
    if not groq_api_key:
        return None

    try:
        # Using a smaller model for speed/cost effectiveness
        model = ChatGroq(model="openai/gpt-oss-20b", temperature=0.7, api_key=groq_api_key)

        json_format = {
            "questions": [
                {
                    "question": "The question text.",
                    "options": {
                        "A": "Option A",
                        "B": "Option B",
                        "C": "Option C",
                        "D": "Option D"
                    },
                    "answer": "The key of the correct option (e.g., 'A')"
                }
            ]
        }
        
        parser = JsonOutputParser(pydantic_object=None)

        prompt = ChatPromptTemplate.from_template(
            """
            You are an expert quiz maker. Your task is to create a multiple-choice quiz based on the user's specifications.

            Subject: {subject}
            Topic: {topic}
            Subtopic: {subtopic}
            Difficulty: {difficulty}
            Number of Questions: {num_questions}

            Please generate the quiz questions. For each question, provide 4 options (A, B, C, D) and indicate the correct answer key.

            IMPORTANT: Respond ONLY with a valid JSON object that strictly follows this structure: {format}.
            """
        )

        chain_pre = prompt | model
        input_data = {
            "subject": subject,
            "topic": topic,
            "subtopic": subtopic if subtopic else "General",
            "difficulty": difficulty,
            "num_questions": num_questions,
            "format": json.dumps(json_format, indent=2)
        }
        
        msg = chain_pre.invoke(input_data)
        
        # ✅ Log Metadata
        log_response_metadata(msg.response_metadata, "Quiz Maker (Generation)")
        c1 = consistency(msg.content)
        # Parse output
        parsed_result = parser.invoke(msg)
        
        # ✅ FIX: Extract the list of questions, don't return the whole dict
        return parsed_result.get("questions", [])

    except Exception as e:
        print(f"Error generating quiz: {e}")
        return None

def generate_explanations(incorrect_questions, difficulty):
    """
    Generates explanations for incorrect answers.
    incorrect_questions: List of dicts {question_text, user_answer, correct_answer}
    """
    if not groq_api_key:
        return {}

    try:
        model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3, api_key=groq_api_key)
        explanations = {}
        
        for item in incorrect_questions:
            prompt = ChatPromptTemplate.from_template(
                """
                You are an expert tutor. A student answered incorrectly.

                Question: "{question}"
                Student's Answer: "{user_answer}"
                Correct Answer: "{correct_answer}"

                Explain why the student's answer is wrong and why the correct answer is right.
                Keep it simple and encouraging for a {difficulty} learner.
                """
            )
            chain = prompt | model
            response = chain.invoke({
                "question": item['question_text'],
                "user_answer": item['user_answer'],
                "correct_answer": item['correct_answer'],
                "difficulty": difficulty
            })
            
            # ✅ Log Metadata
            log_response_metadata(response.response_metadata, "Quiz Maker (Explanation)")
            c2 = consistency(response.content)
            print("[QUIZ MAKER Consistency Value] : ",c2)
            explanations[item['question_text']] = response.content
            
        return explanations
    except Exception as e:
        print(f"Error generating explanations: {e}")
        return {}