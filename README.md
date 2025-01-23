# Steganography via Python

Built in our Year 1 Trimester 2 for our cyber security project that focuses on Steganography by:

1. Image
2. Audio
3. Text

## How does it work

We use LSB bits to help mask the text that is encoded in the image, audio or text file, this is achieved by replaceing the LSB bits with the payload bits. Therefore making the files and contents like messages inside it to be distorted.

111001 (55) [Original] -> 111000 (56) [Modified]

101000 (56) [Original] -> 101001 (41) [Modified]

111001 (55) [Original] -> 111001 (55) 

Therefore making the the bits to show a different type of image, text, audio

