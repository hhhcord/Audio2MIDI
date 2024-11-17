from ClassFiles.AudioLoader import AudioLoader
from ClassFiles.AudioSignalProcessor import AudioSignalProcessor
from ClassFiles.CSV2MIDIConverter import CSV2MIDIConverter
import os

def main():
    # Initialize necessary classes
    audio_loader = AudioLoader()
    audio_processor = AudioSignalProcessor()

    # Configuration parameters
    input_duration_seconds = 27  # Duration of audio input in seconds
    beats_per_minute = 84  # Tempo in beats per minute
    musical_key = "D"  # Key of the audio (e.g., G major)
    is_major_key = True  # Whether the key is major or minor
    midi_output_directory = "output_midi"  # Directory for saving MIDI files

    try:
        # Step 1: Load input audio signal
        print("\nSelect the .wav file for the input audio signal.")
        audio_signal, sample_rate = audio_loader.load_audio(input_duration_seconds)
        print(f"Input audio signal loaded successfully with sample rate: {sample_rate} Hz.")

        # Validate input signal length
        if len(audio_signal) < sample_rate * (60 / beats_per_minute):
            raise ValueError("The input signal is too short for the specified BPM and duration.")

        # Step 2: Process the audio signal and generate CSV files
        print("Processing the audio signal to generate CSV files...")
        audio_processor.process_audio_to_csv(
            input_signal=audio_signal,
            sample_rate=sample_rate,
            bpm=beats_per_minute,
            key=musical_key,
            is_major=is_major_key,
            threshold=38
        )

        # Step 3: Verify CSV files
        csv_files = ["bass.csv", "higher.csv"]
        for csv_file in csv_files:
            if not os.path.exists(csv_file):
                raise FileNotFoundError(f"{csv_file} could not be generated.")

            file_size = os.stat(csv_file).st_size
            if file_size == 0:
                raise ValueError(f"The generated CSV file {csv_file} is empty. Check audio processing.")

        print("CSV files for bass and higher registers generated successfully.")

        # Step 4: Convert the CSV files to MIDI files
        print("Converting CSV files to MIDI files...")
        CSV2MIDIConverter.process_csv_files(
            input_directory=".",  # Current directory containing the CSV files
            output_directory=midi_output_directory,
            tempo=beats_per_minute
        )
        print(f"MIDI files generated successfully in directory: {midi_output_directory}")

    except ValueError as e:
        print(f"\nValueError: {e}")
    except FileNotFoundError as e:
        print(f"\nFileNotFoundError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
