#!/bin/bash

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <YouTube URL>"
    exit 1
fi

# YouTube URL
YOUTUBE_URL=$1

# Download MP3 using yt-dlp command
yt-dlp --extract-audio --audio-format mp3 --audio-quality 0 "$YOUTUBE_URL"
