#!/bin/bash

# Display a file selection dialog
audio_file=$(osascript -e 'POSIX path of (choose file of type {"public.audio"} with prompt "Please select an audio file")')

# Check if a file was selected
if [ -z "$audio_file" ]; then
    echo "No file was selected."
    exit 1
fi

# Set the name of the output file
output_file="${audio_file%.*}_3min_extract.${audio_file##*.}"

# Extract the first 3 minutes using ffmpeg
ffmpeg -i "$audio_file" -t 00:03:00 -c copy "$output_file"

# Completion message
if [ $? -eq 0 ]; then
    echo "Extraction completed. Output file: $output_file"
else
    echo "An error occurred."
fi
