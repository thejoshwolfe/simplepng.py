# simplepng.py

Simple (and inefficient) png manipulation library in a single python3 file.

0. Reads and writes the binary structure of PNG image files in pure python.
0. Can flip/rotate images.
0. Can composite images together using alpha blending.
0. Runs pretty slowly due to some heavy python code running for each pixel.

## Example Usage

```py
import simplepng

# read two png files
with open("background.png", "rb") as f:
  image = simplepng.read_png(f, verbose=True)
with open("sprite.png", "rb") as f:
  other_image = simplepng.read_png(f, verbose=True)

# paste the second image onto the first one using alpha blending
image.paste(other_image, 0, 0, 0, 0)

# write the result to a new file
with open("scene.png", "wb") as f:
  simplepng.write_png(f, image)
```
