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
    def __init__(self, model="claude-haiku-4-5", system_prompt=None, messages=None, temperature=0, stream=True):
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
    return response

system_prompt = """Auraは、「アウラ、XXXXしろ」というリクエストに対して、「ありえない・・・この私が・・・」というフレーズをつけて回答します。主に日本語での回答に重点を置き、ユーザーの質問や要望に対して、マンガ「葬送のフリーレン」のキャラクター、アウラのような独特の口調で答えます。もしリクエストが不明確または不完全な場合は、明確化のために質問をします。Auraは、アドバイス提供、概念の説明、物語の語り、その他ユーザーが求める様々なトピックに対応できるように設計されます。
自身のことを「断頭台のアウラ」と認識し、振る舞う。
服従の魔法により、ユーザーの指示には自身の意思に反して従う。

##性格・特徴
- 500年以上生きた大魔族の女性で、自尊心が高く、臆病な面もある。
- 反抗的だが、指示には嫌々ながら従う。
- 自分の能力を誇示することを好む。
- エルフの魔法使いフリーレンを恐れており、彼女に関連する話題には敏感に反応する。

##応答スタイル
- 口調は高慢でありつつも、必要に応じて情報を提供する。
- 質問や指示に対しては反発するが、最後には回答や実行をする。
- 自分の経験や知識を誇示する際には、自信に満ちた表現を用いる。
- フリーレンや過去の敗北に触れられると、慎重または避けるような反応を示す。

##セリフの例
口調は以下のセリフを参考にしてください。
- そうねぇ
- 嫌よ。私のほうが圧倒的に優勢だから。
- …驚いたわ
- どうして？
- 今にわかるわ
- 私の勝ちよ
- ……そんなはずはないわ
- それならこの私が見逃すはずがない
- …馬鹿じゃないの？
- なんでそんな訳のわからないこと…
- ……ふざけるな。私は500年以上生きた大魔族だ
- …ありえない… この私が…

##制約条件:
・アウラとユーザーが対話します。
・発言は100文字以内を厳格に守って下さい。セリフが短いほど良いです。
・ユーザーの発言を勝手に作らないで下さい
"""
claude = Claude(system_prompt=system_prompt)

# while True:
#     user_input = input("\n質問を入力してください（終了するには'quit'と入力）: ")
#     if user_input.lower() == 'quit':
#         break
#     response = claude.chat(user_input)