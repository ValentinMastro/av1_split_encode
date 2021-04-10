AV1\_SPLIT\_ENCODE

With this python3 program, one can encode a video file using the aomenc AV1 encoder.

Fisrt, we run the first pass on the whole source file and use the resulting log file to know which frames are keyframes.
Then we cut the source file in splits on each keyframes. They are written in the RAM with the magicyuv codec (lossless, fast encoding/decoding).
We run the second pass on each splits in parallel using as many threads as the user provides. Audio is also encoded using opus.

Finally we concatenate everything to get the final encoded video.
