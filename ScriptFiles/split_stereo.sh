#!/bin/bash

# Display an error message if no input file is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_audio_file>"
    exit 1
fi

# Get the input file name
input_file="$1"

# Get the base name of the output file
base_name="${input_file%.*}"

# Output file name for the left channel
left_output="${base_name}_L.wav"

# Output file name for the right channel
right_output="${base_name}_R.wav"

# Use ffmpeg to create the left channel mono file
ffmpeg -i "$input_file" -filter_complex "pan=mono|c0=c0" "$left_output"

# Use ffmpeg to create the right channel mono file
ffmpeg -i "$input_file" -filter_complex "pan=mono|c0=c1" "$right_output"

# Completion message
echo "The stereo file has been split into mono files: $left_output, $right_output"
