import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pyaudio

from audio_utils import create_audio_stream
from vad_utils import VadWrapper
from whisper_utils import WhisperModelWrapper

from claudeStream import process_transcription
from voice import vvox_test

class AudioTranscriber:
    def __init__(self, state_manager):
        self.model_wrapper = WhisperModelWrapper()
        self.vad_wrapper = VadWrapper()
        self.silent_chunks = 0
        self.speech_buffer = []
        self.audio_queue = queue.Queue()
        self.state_manager = state_manager

    async def transcribe_audio(self):
        with ThreadPoolExecutor() as executor:
            while True:
                audio_data_np = await asyncio.get_event_loop().run_in_executor(
                    executor, self.audio_queue.get
                )
                segments = await asyncio.get_event_loop().run_in_executor(
                    executor, self.model_wrapper.transcribe, audio_data_np
                )

                for segment in segments:
                    print(segment.text)
                    response = process_transcription(segment.text)
                    print(f"Claude: {response}")
                    # 音声合成 (同期的に実行されるため、ここでブロックされるが、別スレッドで実行する手もある)
                    # ただし、喋っている間は聞き取りを停止したいので、同期実行で良いかもしれない
                    # あるいは、vvox_test内でstate_managerを操作しているので、非同期に投げても良いが
                    # ここではシンプルに呼び出す。
                    await asyncio.get_event_loop().run_in_executor(
                        executor, vvox_test, response, self.state_manager
                    )

    def process_audio(self, in_data, frame_count, time_info, status):
        # システムが喋っている間は入力を無視する
        if self.state_manager.is_speaking:
            return (in_data, pyaudio.paContinue)

        is_speech = self.vad_wrapper.is_speech(in_data)

        if is_speech:
            self.silent_chunks = 0
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            self.speech_buffer.append(audio_data)
        else:
            self.silent_chunks += 1

        if (
            not is_speech
            and self.silent_chunks > self.vad_wrapper.SILENT_CHUNKS_THRESHOLD
        ):
            if len(self.speech_buffer) > 20:
                audio_data_np = np.concatenate(self.speech_buffer)
                self.speech_buffer.clear()
                self.audio_queue.put(audio_data_np)
import asyncio
import queue
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pyaudio

from audio_utils import create_audio_stream
from vad_utils import VadWrapper
from whisper_utils import WhisperModelWrapper

from claudeStream import process_transcription
from voice import vvox_test

class AudioTranscriber:
    def __init__(self, state_manager):
        self.model_wrapper = WhisperModelWrapper()
        self.vad_wrapper = VadWrapper()
        self.silent_chunks = 0
        self.speech_buffer = []
        self.audio_queue = queue.Queue()
        self.state_manager = state_manager

    async def transcribe_audio(self):
        with ThreadPoolExecutor() as executor:
            while True:
                audio_data_np = await asyncio.get_event_loop().run_in_executor(
                    executor, self.audio_queue.get
                )
                segments = await asyncio.get_event_loop().run_in_executor(
                    executor, self.model_wrapper.transcribe, audio_data_np
                )

                for segment in segments:
                    print(segment.text)
                    response = process_transcription(segment.text)
                    print(f"Claude: {response}")
                    # 音声合成 (同期的に実行されるため、ここでブロックされるが、別スレッドで実行する手もある)
                    # ただし、喋っている間は聞き取りを停止したいので、同期実行で良いかもしれない
                    # あるいは、vvox_test内でstate_managerを操作しているので、非同期に投げても良いが
                    # ここではシンプルに呼び出す。
                    await asyncio.get_event_loop().run_in_executor(
                        executor, vvox_test, response, self.state_manager
                    )

    def process_audio(self, in_data, frame_count, time_info, status):
        # システムが喋っている間は入力を無視する
        if self.state_manager.is_speaking:
            return (in_data, pyaudio.paContinue)

        is_speech = self.vad_wrapper.is_speech(in_data)

        if is_speech:
            self.silent_chunks = 0
            audio_data = np.frombuffer(in_data, dtype=np.int16)
            self.speech_buffer.append(audio_data)
        else:
            self.silent_chunks += 1

        if (
            not is_speech
            and self.silent_chunks > self.vad_wrapper.SILENT_CHUNKS_THRESHOLD
        ):
            if len(self.speech_buffer) > 20:
                audio_data_np = np.concatenate(self.speech_buffer)
                self.speech_buffer.clear()
                self.audio_queue.put(audio_data_np)
            else:
                # noise clear
                self.speech_buffer.clear()

        return (in_data, pyaudio.paContinue)

    def start_transcription(self, selected_device_index):
        stream = create_audio_stream(selected_device_index, self.process_audio)
        stream.start_stream()
        print("Listening...")
        try:
            asyncio.run(self.transcribe_audio())
        except KeyboardInterrupt:
            print("Interrupted.")
        finally:
            stream.stop_stream()
            stream.close()