# プロジェクト名
対話型アシスタント

# 動作の流れ
faster-whisper → claude → (voiceBox) tts

# 使い方
このプロジェクトは `uv` を使用して管理されています。

1. **セットアップ**:
   ```bash
   # uvがインストールされていない場合
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # 依存関係の同期
   uv sync
   ```

2. **実行**:
   ```bash
   uv run main.py
   ```

# 作成方法・参考
- https://qiita.com/reriiasu/items/920227cf604dfb8b7949 (faster-whisper)
- https://okumuralab.org/~okumura/python/claude_api.html (Claude API)
- https://note.com/key410/n/n1bf0e797da61 (VOICEVOX API)

# 変更点・改善内容
## 最新のアップデート
- **環境管理**: `uv` に移行し、依存関係管理を現代化しました。
- **リファクタリング**: `StateManager` を導入し、音声認識と音声合成の状態管理を分離・改善しました。
- **割り込み機能**: システムが発話中（TTS再生中）は音声認識を一時停止する機能を実装しました（README 旧項目の2番を解決）。

## 構成
- `main.py`: エントリーポイント
- `audio_transcriber.py`: 音声認識と全体の制御
- `claudeStream.py`: Claudeとの対話処理
- `voice.py`: VOICEVOXによる音声合成
- `state_manager.py`: 状態管理（発話中フラグなど）

# 今後の修正予定箇所
1. ~~python main.pyでプログラムを実行時、"質問を入力してください..."と出力されてしまうバグを修正~~ Fixed
2. ~~合成音声の出力時に音声認識機能を一時停止させるか、対話の割り込み処理を組み込む~~ Implemented
3. AIのキャラクターの方針を決めて、緻密なシステムプロンプトの作成
4. TTSをstyle-bert-vits-2で作成した合成音声モデルに変更する
5. pythonのapiサーバーを立てて別のデバイスからでも実行できるようにする
6. テキスト処理をclaudeからローカルLLMのモデルに変更する
7. audio入力を他のデバイスからでも行えるようにする
8. コードの最適化 (進行中: リファクタリング実施済み)
9. 話者分離機能の追加
10. vadについて深く調べ、無音区間のハルシネーションの改善に取り組む

# Credit
このプロジェクトには、奥村晴彦先生のコードが含まれています。元のコードは[こちら](https://okumuralab.org/~okumura/python/claude_api.html)からアクセスできます。このコンテンツは[クリエイティブ・コモンズ 表示 4.0 国際ライセンス](https://creativecommons.org/licenses/by/4.0/)のもとで提供されています。

# License
MIT
This software is released under the MIT License, see LICENSE.txt.