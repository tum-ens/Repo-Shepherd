import google.generativeai as genai
from together import Together
import time

def gemini_api(prompt: str, model) -> str:
    """
    Get answer via API of gemini.
    NOTICE: time.sleep(5) is to avoid reach rate limit per minutes, this can be deleted if there's a pro account.
    :param prompt: the given prompt to LLM-gemini.
    :return: the answer from LLM.
    """
    response = model.generate_content(prompt)
    result = response.text.strip()
    # Request per minute is 15, sleep for 5 seconds can avoid crash.
    time.sleep(5)
    return result

def together_api(prompt: str) -> str:
    from together import Together

    client = Together(api_key="0b70b715657d1ed30b062c0fd53764d2c0a04ee98c51a38ccc6577dee323dec0")

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-8B-Instruct-Turbo",
        messages=[{"role": "user", 
                   "content": prompt}],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    prompt = "whats the capital of france?"
    print (together_api(prompt))
