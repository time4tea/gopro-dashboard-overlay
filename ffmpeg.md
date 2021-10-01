### Useful FFMPEG Commands


## Extract some section of a file

ffmpeg -i <input>> -ss <start hh:mm:ss> -to <end hh:mm:ss> -c copy output.mp4

## Scale 1080p to 720p 

ffmpeg -i <input> -vf scale=-1:720 <output>

