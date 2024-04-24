# プロジェクト名
対話型アシスタント

# 動作の流れ
faster-whisper → claude → (vert-vits-2 or voiceBox) ttsは今後実装予定

# 使い方
1. venvの仮想環境を有効化する ".\sttest\Scripts\activate" windows版
". sttest/bin/activate" mac版  
2. python main.py と入力して実行

# 作成方法
https://qiita.com/reriiasu/items/920227cf604dfb8b7949  
↑ faster-whisperを使ったSTT  
https://okumuralab.org/~okumura/python/claude_api.html  
↑ claude 3を使ったchatbotのサンプル  
https://note.com/key410/n/n1bf0e797da61  
↑　voicebox apiを使った合成音声のサンプル  
これらをベースに組み合わせて作ってみた

# 変更点
STT編  
1. claudeStream.pyに新しい関数を追加して、文字起こしされたテキストをaudio_transcriber.pyから受け取って処理するようにした  
def process_transcription(text):  
    response = claude.chat(text)  
    return response  

2. audio_transcriber.pyのtranscribe_audioメソッド内で、claudeStream.pyのprocess_transcription関数を呼び出す  
from claudeStream import process_transcription　#このモジュールをインポートする  

async def transcribe_audio(self):  
    ...  
    for segment in segments:  
        print(segment.text)  
        response = process_transcription(segment.text)  

TTS編  
1. claudeStream.pyのprocess_transcription関数を修正し、Claudeからの応答をvoice.pyのvvox_test関数に渡す  
from voice import vvox_test  

def process_transcription(text):  
    response = claude.chat(text)  
    vvox_test(response)  # Claudeの応答をvvox_testに渡す  
    return response  


# 今後の修正予定箇所
1. ~~python main.pyでプログラムを実行時、"質問を入力してください（終了するには'quit'と入力）:" と出力されてしまうバグを修正~~ Fixed
2. 合成音声の出力時に音声認識機能を一時停止させるか、対話の割り込み処理を組み込む
3. AIのキャラクターの方針を決めて、緻密なシステムプロンプトの作成
4. TTSをstyle-bert-vits-2で作成した合成音声モデルに変更する
5. pythonのapiサーバーを立てて別のデバイスからでも実行できるようにする
6. テキスト処理をclaudeからローカルLLMのモデルに変更する
7. audio入力を他のデバイスからでも行えるようにする
8. コードの最適化
9. 話者分離機能の追加　←speakerから再生されている合成音声と人が喋っている声を区別させるため
10. vadについて深く調べ、無音区間のハルシネーションの改善に取り組む

# Credit
このプロジェクトには、奥村晴彦先生のコードが含まれています。元のコードは[こちら](https://okumuralab.org/~okumura/python/claude_api.html)からアクセスできます。このコンテンツは[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/)のもとで提供されています。

# Licence
MIT
This software is released under the MIT License, see LICENSE.txt.