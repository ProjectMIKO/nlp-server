import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Create a Flask app
app = Flask(__name__)


@app.route('/keyword', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get("message")

        if not user_message:
            return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400

        # GPT 모델에 요약 요청
        prompt = f"다음 회의 내용을 하나의 키워드로 요약해줘:\n\n{user_message}\n\n하나의 키워드:"

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-3.5-turbo",
        )
        response_message = chat_completion.choices[0].message.content.strip()

        return jsonify({"response": response_message}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
