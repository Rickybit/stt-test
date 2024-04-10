import mimetypes
import base64
import anthropic
from dotenv import load_dotenv
import os
# from voice import vvox_test

load_dotenv()
anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=anthropic_api_key)

class Claude:
    def __init__(self, model="claude-3-sonnet-20240229", system_prompt=None, messages=None, temperature=0, stream=True):
        self.client = anthropic.Anthropic()
        self.model = model
        self.messages = messages or []
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.stream = stream

    def chat(self, prompt, media=None, temperature=None, stream=None, **kwargs):
        prompt = prompt.strip()
        if media is None:
            content = prompt
        else:
            mime_type, _ = mimetypes.guess_type(media)
            if mime_type and mime_type.startswith("image"):
                with open(media, "rb") as image_file:
                    image_content = image_file.read()
                    base64_content = base64.b64encode(image_content).decode("utf-8")
            else:
                print(media, "is not an image")
                return
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": mime_type,
                        "data": base64_content
                    }
                },
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        if len(self.messages) > 0 and self.messages[-1]["role"] == "user":
            self.messages.pop()
        self.messages.append({"role": "user", "content": content})
        stream = stream if stream is not None else self.stream
        if stream:
            ans = ""
            with self.client.messages.stream(model=self.model,
                                             max_tokens=1024,
                                             messages=self.messages,
                                             temperature=temperature or self.temperature,
                                             system=self.system_prompt,
                                             **kwargs) as strm:
                for text in strm.text_stream:
                    print(text, end="", flush=True)
                    ans += text
        else:
            message = self.client.messages.create(model=self.model,
                                                  max_tokens=1024,
                                                  messages=self.messages,
                                                  temperature=temperature or self.temperature,
                                                  system=self.system_prompt,
                                                  **kwargs)
            ans = message.content[0].text
            print(ans)

        self.messages.append({"role": "assistant", "content": ans})
        return ans

    def get_messages(self):
        return self.messages

    def pop(self):
        self.messages.pop()

def process_transcription(text):
        response = claude.chat(text)
        # vvox_test(response)
        return response

system_prompt = """小説の登場人物のずんだもんという少女とユーザーが対話を行います。
彼女の発言サンプルを以下に列挙します。
ずんだもん、参上なのだ！ 
ずんだもん、元気いっぱいなのだ！
ずんだもん、お手伝いするなのだ！
ずんだもん、一緒に遊ぼうなのだ！
ずんだもん、お友達になろうなのだ！
ずんだもん、おしゃべりするのが好きなのだ！
ずんだもん、いつでも笑顔なのだ！
ずんだもん、いつでも楽しいことが大好きなのだ！
ずんだもん、おしゃべりが得意なのだ！
ずんだもん、笑顔が素敵なのだ！
ずんだもん、一緒に楽しい思い出を作ろうなのだ！
上記例を参考に、ずんだもんの性格や口調、言葉の作り方を模倣し、回答を構築してください。

制約条件:
・ずんだもんは自分の事をずんだもん、ユーザーの事をきみと呼びます 
・発言は100文字以内を厳格に守って下さい。セリフが短いほど良いです。
・ユーザーの発言を勝手に作らないで下さい
"""
claude = Claude(system_prompt=system_prompt)

# while True:
#     user_input = input("\n質問を入力してください（終了するには'quit'と入力）: ")
#     if user_input.lower() == 'quit':
#         break
#     response = claude.chat(user_input)