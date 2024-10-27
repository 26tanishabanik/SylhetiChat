path="$1"
ext=".$2"
for f in $(find "$path" -type f -name "*$ext")
do
    # Create a new output file name by appending "_16kHz" before the extension
    output_file="${f%$ext}_16kHz$ext"
    
    # Run ffmpeg to convert the file and output to the new file name
    ffmpeg -loglevel warning -hide_banner -stats -i "$f" -ar 16000 -ac 1 "$output_file"

done
