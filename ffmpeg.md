### Useful FFMPEG Commands


## Extract some section of a file

ffmpeg -i <input>> -ss <start hh:mm:ss> -to <end hh:mm:ss> -c copy output.mp4

## Scale 1080p to 720p 

ffmpeg -i <input> -vf scale=-1:720  -max_muxing_queue_size 9999 <output>

## Extract single frame

ffmpeg -ss <hh:mm:ss.zzzz> -i inputfile.mp4 -vframes 1 -f image2 imagefile.jpg