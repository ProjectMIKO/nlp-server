from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from config.config import OPENAI_API_KEY
from util.cost_calculator import calculate_cost

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)

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

        print(f"요청 내용: \n{user_message}")
        # gpt 요청 비용 계산
        cost = calculate_cost(chat_completion)
        print(f"Cost: ${cost:.5f}")

        return jsonify({"keyword": response_message, "cost": cost}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
