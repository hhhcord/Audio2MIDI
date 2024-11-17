import re  # Module for handling regular expressions.
import os  # Module for file and directory operations.
import argparse  # Module for parsing command-line arguments.
from fractions import Fraction  # Module for handling fractions.
import music21  # Library for music data manipulation.
import pandas as pd  # Library for data analysis and manipulation.

class CSV2MIDIConverter:
    """Class to convert CSV files to MIDI files."""
    
    # Mapping of note names to MIDI numeric values.
    NOTE_NAMES = ['C', 'D-', 'D', 'E-', 'E', 'F', 'G-', 'G', 'A-', 'A', 'B-', 'B']
    NOTE_TO_NUMBER = {note: index for index, note in enumerate(NOTE_NAMES)}
    NOTE_ALIASES = {'A#': 'B-', 'C#': 'D-', 'D#': 'E-', 'F#': 'G-', 'G#': 'A-'}
    
    @staticmethod
    def split_note(note):
        """Splits a musical note into its base name and octave."""
        assert re.fullmatch(r'[A-G](#|-)?[0-7]', note), 'Invalid note format.'
        return note[:-1], int(note[-1])
    
    @staticmethod
    def note_to_midi_number(note_name):
        """Converts a note name to its MIDI numeric value."""
        note, octave = CSV2MIDIConverter.split_note(note_name)
        note_number = CSV2MIDIConverter.NOTE_TO_NUMBER.get(CSV2MIDIConverter.NOTE_ALIASES.get(note, note))
        return (octave + 1) * 12 + note_number

    @staticmethod
    def create_midi_file(csv_filename, data_frame, tempo, output_directory):
        """Creates a MIDI file from a DataFrame containing musical data."""
        midi_stream = music21.stream.Stream()
        midi_stream.append(music21.tempo.MetronomeMark(number=tempo))
        running_offset = 0

        for _, row in data_frame.iterrows():
            note_duration = row.iloc[3]
            note = music21.note.Note(
                CSV2MIDIConverter.note_to_midi_number(row.iloc[1]),
                duration=music21.duration.Duration(Fraction(note_duration))
            )
            note.volume.velocity = row.iloc[4]
            note.offset = row.iloc[2] + running_offset
            midi_stream.insert(note)

        output_path = os.path.join(output_directory, csv_filename.replace(".csv", ".mid"))
        midi_stream.write("midi", output_path)

    @staticmethod
    def validate_directory(directory_name):
        """Validates if the given path is a directory."""
        if not os.path.isdir(directory_name):
            raise argparse.ArgumentTypeError(f"{directory_name} is not a directory.")
        return directory_name

    @staticmethod
    def process_csv_files(input_directory, output_directory=None, tempo=None):
        """Processes all CSV files in the input directory and converts them to MIDI files."""
        if not output_directory:
            output_directory = f"{input_directory}-output-midis"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for file_name in os.listdir(input_directory):
            if file_name.endswith(".csv"):
                file_path = os.path.join(input_directory, file_name)
                data_frame = pd.read_csv(file_path, engine='python')
                file_tempo = data_frame.iloc[1, 5] if tempo is None else tempo
                CSV2MIDIConverter.create_midi_file(file_name, data_frame, file_tempo, output_directory)

    @staticmethod
    def parse_command_line_arguments():
        """Parses command-line arguments."""
        parser = argparse.ArgumentParser(description="Convert CSV files to MIDI files.")
        parser.add_argument("input_directory", type=str, help="Directory containing input CSV files.")
        parser.add_argument("-o", "--output_directory", type=str, help="Directory to save output MIDI files.")
        parser.add_argument("-t", "--tempo", type=int, help="Tempo for the MIDI files.")
        return parser.parse_args()

    @staticmethod
    def main():
        """Main function to execute the conversion process."""
        args = CSV2MIDIConverter.parse_command_line_arguments()
        CSV2MIDIConverter.validate_directory(args.input_directory)
        CSV2MIDIConverter.process_csv_files(args.input_directory, args.output_directory, args.tempo)

'''
# Execute the script if run as a standalone program.
if __name__ == "__main__":
    CSV2MIDIConverter.main()
'''
