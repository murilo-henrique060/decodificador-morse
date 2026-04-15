import pyaudio
import numpy as np
from time import perf_counter
from PySide6.QtCore import QThread

from utils.morse import morse_to_text
from utils.freq_filter import filter_frequencies

TIME_UNIT = 0.06  # Unidade base em segundos (60 ms)

DOT = TIME_UNIT         # Limite para identificar ponto
DASH = TIME_UNIT * 3    # Limite para identificar traço

SIGNAL_GAP = TIME_UNIT # Tempo de silêncio entre sinais
LETTER_GAP = TIME_UNIT * 3    # Tempo de silêncio entre letras
WORD_GAP = TIME_UNIT * 7    # Tempo de silêncio entre palavras

# Limites para identificar sinais e espaços com base nos tempos
DOT_DASH_LIMIT = (DOT + DASH) / 2 # Limite para diferenciar ponto de traço (90 ms)
SIGNAL_LETTER_GAP_LIMIT = (SIGNAL_GAP + LETTER_GAP * 1.5) / 2 # Limite para diferenciar sinal de letra (180 ms)
LETTER_WORD_GAP_LIMIT = (LETTER_GAP + WORD_GAP) / 2 # Limite para diferenciar letra de palavra (240 ms)

class DecoderController(QThread):
    def __init__(self, active=False, chunk=1024, rate=44100, interval=3, threshold=6000):
        super().__init__()

        self._p = pyaudio.PyAudio()
        
        self._active = active
        self._filter_frequencies = False

        self._stream = None
        self._raw_data = np.ndarray([0], dtype=np.int16)
        self._clean_data = np.ndarray([0], dtype=np.int16)

        self.chunk = chunk
        self.threshold = threshold
        self.rate = rate
        self.interval = interval

        self._current_signal = ""
        self._morse_str = ""

        self._last_state = False
        self._start_time = None


    @property
    def active(self):
        return self._active
    

    @property
    def chunk(self):
        return self._chunk
    
    @chunk.setter
    def chunk(self, value):
        self._chunk = value
        self._initialize_audio_stream()


    @property
    def threshold(self):
        return self._threshold
    
    @threshold.setter
    def threshold(self, value):
        self._threshold = value


    @property
    def rate(self):
        return self._rate
    
    @rate.setter
    def rate(self, value):
        self._rate = value
        self._initialize_audio_stream()


    @property
    def interval(self):
        return self._interval
    
    @interval.setter
    def interval(self, value):
        self._interval = value
        self._resize_data_buffer()


    @property
    def buffer_size(self):
        return self.rate * self.interval # número de amostras para o intervalo definido (3 segundos por padrão)
    

    @property
    def raw_data(self):
        return self._raw_data
    
    @property
    def clean_data(self):
        return self._clean_data


    @property
    def morse_str(self):
        return self._morse_str + self._current_signal

    @property
    def text_str(self):
        return morse_to_text(self.morse_str)


    def _initialize_audio_stream(self):
        if not self._active:
            return

        if self._stream is not None:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        try:
            self._stream = self._p.open(format=pyaudio.paInt16, channels=1, rate=self.rate, input=True, frames_per_buffer=self.chunk)
        except Exception as e:
            print(f"Erro ao abrir o stream de áudio: {e}")
            self._stream = None

    def _resize_data_buffer(self):
        new_buffer_size = self.buffer_size
        if len(self.raw_data) != new_buffer_size:
            self._raw_data = np.resize(self._raw_data, new_buffer_size)
            self._clean_data = np.resize(self._clean_data, new_buffer_size)


    def start(self):
        self._active = True
        self._start_time = perf_counter()
        self._initialize_audio_stream()

        super().start()

    def stop(self):
        self._active = False
        if self._stream is not None:
            self._stream.stop_stream()

    def reset(self):
        self._morse_str = ""
        self._current_signal = ""
        self._last_state = False

        self._raw_data = np.ndarray([0], dtype=np.int16)
        self._clean_data = np.ndarray([0], dtype=np.int16)
        self._resize_data_buffer()

        self._start_time = perf_counter()

    def close(self):
        self.stop()
        if self._stream is not None:
            self._stream.close()
            self._stream = None

        self._p.terminate()


    def _get_audio_block(self):
        if self._stream is None:
            return np.zeros(self.chunk, dtype=np.int16)

        try:
            block = np.frombuffer(self._stream.read(self.chunk, exception_on_overflow=False), dtype=np.int16)

            if self._filter_frequencies:
                block = filter_frequencies(block, self.rate, 400, 480) # Exemplo de filtro entre 400 Hz e 480 Hz

            return block
        except Exception as e:
            print(f"Erro ao ler o stream de áudio: {e}")
            return np.zeros(self.chunk, dtype=np.int16)

    def _update_current_signal(self, is_on, duration):
        if is_on:
            if duration < DOT_DASH_LIMIT:
                self._current_signal = "."
            else:
                self._current_signal = "-"
        elif self._morse_str != "":
            if duration < SIGNAL_LETTER_GAP_LIMIT:
                self._current_signal = ""
            elif duration < LETTER_WORD_GAP_LIMIT:
                self._current_signal = " "
            else:
                self._current_signal = " / "

    def _push_signal(self):
        if self._current_signal:
            self._morse_str += self._current_signal
            self._current_signal = ""


    def run(self):
        while self.active:
            block = self._get_audio_block()

            self._raw_data = np.roll(self._raw_data, -self.chunk)
            self._raw_data[-self.chunk:] = block

            is_on = np.max(np.abs(block)) > self.threshold
            self._clean_data = np.roll(self._clean_data, -self.chunk)
            self._clean_data[-self.chunk:] = 1 if is_on else 0

            now = perf_counter()
            duration = now - self._start_time # type: ignore
        
            self._update_current_signal(self._last_state, duration)

            if is_on != self._last_state:
                self._push_signal()

                self._start_time = now
                self._last_state = is_on