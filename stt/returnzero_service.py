import os
from dotenv import load_dotenv
import json
import requests
import time
import threading

# .env 파일 로드
load_dotenv()

access_token = None
token_expiry_time = None
token_lock = threading.Lock()


def get_access_token():
    print("\n리턴제로 토큰 요청 시작")
    global access_token, token_expiry_time
    with token_lock:
        if access_token and token_expiry_time and time.time() < token_expiry_time:
            return access_token

    client_id = os.getenv("RT_CLIENT_ID")
    client_secret = os.getenv("RT_CLIENT_SECRET")
    auth_resp = requests.post(
        'https://openapi.vito.ai/v1/authenticate',
        data={
            'client_id': client_id,
            'client_secret': client_secret
        }
    )
    auth_resp.raise_for_status()
    access_token = auth_resp.json()['access_token']
    token_expiry_time = time.time() + 3600 * 6  # assuming token is valid for 6 hour
    return access_token


def request_text(file):
    print("\n리턴제로 요청 시작")
    try:
        access_token = get_access_token()

        config = {
            "use_diarization": False,
            "use_itn": True,
            "use_disfluency_filter": False,
            "use_profanity_filter": False,
            "use_paragraph_splitter": False,
            "paragraph_splitter": {"max": 50}
        }

        file.seek(0)
        files = {
            'config': (None, json.dumps(config), 'application/json'),
            'file': (file.filename, file, file.content_type)
        }

        transcribe_resp = requests.post(
            'https://openapi.vito.ai/v1/transcribe',
            headers={'Authorization': 'bearer ' + access_token},
            files=files
        )
        transcribe_resp.raise_for_status()
        response_json = transcribe_resp.json()
        transcription_id = response_json['id']

        status_url = f'https://openapi.vito.ai/v1/transcribe/{transcription_id}'
        timeout = time.time() + 300  # 5 minutes from now
        while True:
            if time.time() > timeout:
                raise Exception("Transcription request timed out")

            status_resp = requests.get(
                status_url,
                headers={'Authorization': 'bearer ' + access_token}
            )
            status_resp.raise_for_status()
            status_data = status_resp.json()
            print(f"Status Data: {status_data}")

            if status_data['status'] == 'completed':
                script = ' '.join([utterance['msg'] for utterance in status_data['results']['utterances']])
                return status_resp.status_code, script
            elif status_data['status'] == 'failed':
                return status_resp.status_code, "Transcription failed"
            else:
                time.sleep(5)

    except requests.RequestException as e:
        return 500, f"Request error: {str(e)}"
    except Exception as e:
        return 500, f"Unexpected error: {str(e)}"
