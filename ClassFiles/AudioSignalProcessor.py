import numpy as np
import pandas as pd
import re

class AudioSignalProcessor:
    """
    A class to process audio signals and convert them into musical note data in CSV format.
    The system extracts bass and higher register notes based on a given key and mode (major/minor).
    """
    NOTE_NAMES = ['C', 'D-', 'D', 'E-', 'E', 'F', 'G-', 'G', 'A-', 'A', 'B-', 'B']
    NOTE_TO_NUMBER = {note: index for index, note in enumerate(NOTE_NAMES)}
    NOTE_ALIASES = {'A#': 'B-', 'C#': 'D-', 'D#': 'E-', 'F#': 'G-', 'G#': 'A-'}
    A440 = 440.0  # Hz for A4
    MIN_FREQ = 30  # Minimum frequency for bass
    MAX_FREQ = 4186  # Maximum frequency for higher range

    def __init__(self):
        pass

    @staticmethod
    def split_note(note):
        try:
            assert re.fullmatch(r'[A-G](#|-)?[0-7]', note), 'Invalid note format.'
            return note[:-1], int(note[-1])
        except AssertionError as e:
            raise ValueError(f"Invalid note format: {note}. Must match [A-G](#|-)?[0-7].")

    @staticmethod
    def bpm_to_sixteenth_duration(bpm):
        if bpm <= 0:
            raise ValueError("BPM must be greater than 0.")
        return 15 / bpm

    @staticmethod
    def fft_by_sixteenth(input_signal, sample_rate, sixteenth_duration):
        segment_size = int(sixteenth_duration * sample_rate)
        if segment_size <= 0:
            raise ValueError("Segment size must be greater than 0.")
        if len(input_signal) < segment_size:
            raise ValueError("Input signal is too short for the given BPM and sample rate.")

        segments = [input_signal[i:i + segment_size] for i in range(0, len(input_signal), segment_size)]
        fft_results = [20 * np.log10(np.abs(np.fft.rfft(segment)) + 1e-50) for segment in segments]

        if not fft_results or any(len(result) == 0 for result in fft_results):
            raise ValueError("FFT results are empty or invalid.")
        return fft_results

    @staticmethod
    def apply_filter(fft_results, sampling_rate):
        filter_results = []
        for result in fft_results:
            frequencies = np.fft.rfftfreq(len(result) * 2 - 1, d=1.0 / sampling_rate)
            filter_curve = 3 * np.log2(frequencies / AudioSignalProcessor.A440 + 1e-50)
            filter_results.append(result + filter_curve)
        return filter_results

    @staticmethod
    def calculate_scale_frequencies(key, is_major):
        major_intervals = [0, 2, 4, 5, 7, 9, 11]
        minor_intervals = [0, 2, 3, 5, 7, 8, 10]
        intervals = major_intervals if is_major else minor_intervals

        if key not in AudioSignalProcessor.NOTE_TO_NUMBER:
            raise ValueError(f"Invalid key: {key}. Must be one of {AudioSignalProcessor.NOTE_NAMES}.")

        key_index = AudioSignalProcessor.NOTE_TO_NUMBER[key]
        scale_frequencies = []
        for octave in range(0, 8):
            for interval in intervals:
                midi_number = key_index + interval + (octave * 12)
                frequency = AudioSignalProcessor.A440 * 2 ** ((midi_number - 69) / 12)
                scale_frequencies.append(frequency)

        bass_frequencies = [freq for freq in scale_frequencies if AudioSignalProcessor.MIN_FREQ <= freq <= 200]
        higher_frequencies = [freq for freq in scale_frequencies if 200 < freq <= AudioSignalProcessor.MAX_FREQ]

        if not bass_frequencies:
            raise ValueError("No frequencies found in bass range.")
        if not higher_frequencies:
            raise ValueError("No frequencies found in higher range.")

        return bass_frequencies, higher_frequencies

    @staticmethod
    def extract_amplitudes(fft_results, scale_frequencies, sampling_rate):
        amplitudes = []
        for fft_result in fft_results:
            # print('fft_result: ', fft_result)
            fft_frequencies = np.fft.rfftfreq(len(fft_result) * 2 - 1, d=1.0 / sampling_rate)
            # print('fft_frequencies', fft_frequencies)
            time_step_amplitudes = []
            for freq in scale_frequencies:
                # print('freq: ', freq)
                if len(fft_frequencies) == 0:
                    raise ValueError("FFT frequencies are empty.")
                closest_index = np.argmin(np.abs(fft_frequencies - freq))
                time_step_amplitudes.append(fft_result[closest_index])
            amplitudes.append(time_step_amplitudes)

        if not all(isinstance(a, list) for a in amplitudes):
            raise ValueError("extract_amplitudes must return a list of lists.")
        return amplitudes

    @staticmethod
    def generate_csv_data(frequencies, amplitudes, bpm, threshold):
        """
        Generates data for CSV output, using beats for start_time and duration.
        """
        # Validate input data
        if not isinstance(frequencies, list) or not all(isinstance(f, list) for f in frequencies):
            raise ValueError("Frequencies must be a list of lists.")
        if not isinstance(amplitudes, list) or not all(isinstance(a, list) for a in amplitudes):
            raise ValueError("Amplitudes must be a list of lists.")

        beats_per_sixteenth = 1 / 4  # Each sixteenth note is 1/4 of a beat
        csv_data = []

        for time_idx, (freq_list, amp_list) in enumerate(zip(frequencies, amplitudes)):
            if not isinstance(freq_list, list) or not isinstance(amp_list, list):
                raise ValueError(f"Invalid data at time index {time_idx}: frequencies and amplitudes must be lists.")
            for freq, amp in zip(freq_list, amp_list):
                note_name = AudioSignalProcessor.frequency_to_note_name(freq)
                # print('freq: ', freq)
                # print('amp: ', amp)
                csv_data.append({
                    'index': time_idx,
                    'note_name': note_name,
                    'start_time': time_idx * beats_per_sixteenth,  # Time in beats
                    'duration': beats_per_sixteenth,  # Duration in beats
                    'velocity': 100 if amp > threshold else 0,
                    'tempo': bpm
                })
        return csv_data

    @staticmethod
    def frequency_to_note_name(freq):
        """
        Converts a frequency to its corresponding note name.
        """
        note_number = int(round(12 * np.log2(freq / AudioSignalProcessor.A440) + 69))
        octave = note_number // 12 - 1
        note_index = note_number % 12
        return f"{AudioSignalProcessor.NOTE_NAMES[note_index]}{octave}"

    def process_audio_to_csv(self, input_signal, sample_rate, bpm, key, is_major, threshold):
        """
        Main method to process audio and generate CSV files for bass and higher registers.
        """
        sixteenth_duration = self.bpm_to_sixteenth_duration(bpm)
        fft_results = self.fft_by_sixteenth(input_signal, sample_rate, sixteenth_duration)
        filtered_results = self.apply_filter(fft_results, sample_rate)

        bass_freqs, higher_freqs = self.calculate_scale_frequencies(key, is_major)
        bass_amplitudes = self.extract_amplitudes(filtered_results, bass_freqs, sample_rate)
        # print('bass_amplitudes',bass_amplitudes)
        higher_amplitudes = self.extract_amplitudes(filtered_results, higher_freqs, sample_rate)
        # print('higher_amplitudes',higher_amplitudes)

        if not bass_amplitudes:
            raise ValueError("No data in bass amplitudes.")
        if not higher_amplitudes:
            raise ValueError("No data in higher amplitudes.")

        # Adjust frequencies to be a list of lists matching the structure of amplitudes
        bass_frequencies = [bass_freqs] * len(bass_amplitudes)
        higher_frequencies = [higher_freqs] * len(higher_amplitudes)

        bass_csv_data = self.generate_csv_data(bass_frequencies, bass_amplitudes, bpm, threshold)
        higher_csv_data = self.generate_csv_data(higher_frequencies, higher_amplitudes, bpm, threshold)

        pd.DataFrame(bass_csv_data).to_csv("bass.csv", index=False)
        pd.DataFrame(higher_csv_data).to_csv("higher.csv", index=False)
        print("CSV files generated: bass.csv and higher.csv")
