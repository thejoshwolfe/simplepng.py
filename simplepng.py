# this is python 3, not python 2

__all__ = ["read_png", "write_png", "ImageBuffer", "SimplePngError"]

import struct
import zlib
import sys
import time
import collections

# adapted from http://stackoverflow.com/a/25835368/367916

magic_number = b"\x89PNG\r\n\x1A\n"

IHDR_fmt = "!IIBBBBB"
color_type_mask_INDEXED = 1
color_type_mask_COLOR = 2
color_type_mask_ALPHA = 4

def I4(value):
  return struct.pack("!I", value)

def write_png(f, image):
  height = image.height
  width = image.width

  f.write(magic_number)

  # IHDR
  color_type = color_type_mask_COLOR | color_type_mask_ALPHA
  bit_depth = 8
  compression = 0
  filter_method = 0
  interlaced = 0
  IHDR = struct.pack(IHDR_fmt, width, height, bit_depth, color_type, compression, filter_method, interlaced)
  Chunk(b"IHDR", IHDR).write_to(f)

  # IDAT
  raw = []
  for y in range(height):
    raw.append(b"\x01") # filter type is difference from previous value
    previous_value = 0
    for x in range(width):
      value = image.data[y * width + x]
      raw.append(I4(subtract_bytes(value, previous_value)))
      previous_value = value
  raw = b"".join(raw)
  compressor = zlib.compressobj()
  compressed = compressor.compress(raw)
  compressed += compressor.flush()
  block = b"IDAT" + compressed
  f.write(I4(len(compressed)) + block + I4(zlib.crc32(block)))

  # IEND
  block = b"IEND"
  f.write(I4(0) + block + I4(zlib.crc32(block)))

class Chunk:
  def __init__(self, type_code, body):
    self.type_code = type_code
    self.body = body
  def write_to(self, f):
    block = self.type_code + self.body
    f.write(I4(len(self.body)) + block + I4(zlib.crc32(block)))
def read_chunk(f):
  try:
    [length] = struct.unpack("!I", f.read(4))
    type_code = f.read(4)
    body = f.read(length)
    if len(body) < length:
      raise SimplePngError("unexpected EOF")
    crc32 = struct.unpack("!I", f.read(4))
  except struct.error:
    raise SimplePngError("unexpected EOF")
  return Chunk(type_code, body)

class ImageBuffer:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    # data is formatted 0xRRGGBBAA in row-major order
    self.data = [0] * (width * height)
  def set(self, x, y, value):
    self.data[y * self.width + x] = value
  def at(self, x, y):
    return self.data[y * self.width + x]
  def paste(self, other, sx=0, sy=0, dx=0, dy=0, width=None, height=None, flip_h=False, rotate=0):
    if width == None:
      width = min(self.width - dx, other.width - sx)
    if height == None:
      height = min(self.height - dy, other.height - sy)
    if flip_h or rotate != 0:
      other = other.copy(sx=sx, sy=sy, width=width, height=height)
      sx = 0
      sy = 0
      if flip_h: other.flip_h()
      if rotate != 0: other.rotate(rotate)
    for y in range(height):
      for x in range(width):
        value = other.at(sx + x, sy + y)
        alpha = value & 0xff
        if alpha == 0:
          continue
        if alpha < 255:
          value = alpha_blend(value, self.at(dx + x, dy + y))
        self.set(dx + x, dy + y, value)
  def copy(self, sx=0, sy=0, width=None, height=None):
    if width == None: width = self.width
    if height == None: height = self.height
    other = ImageBuffer(width, height)
    for y in range(height):
      for x in range(width):
        other.set(x, y, self.at(x + sx, y + sy))
    return other
  def flip_h(self):
    for y in range(self.height):
      for x in range(self.width // 2):
        x2 = self.width - 1 - x
        tmp = self.at(x, y)
        self.set(x, y, self.at(x2, y))
        self.set(x2, y, tmp)
  def rotate(self, quarter_turns):
    for y in range(self.height // 2):
      y2 = self.height - 1 - y
      for x in range(self.width // 2):
        x2 = self.width - 1 - x
        tmp = self.at(x, y)
        if quarter_turns == 1:
          self.set(x, y, self.at(y, x2))
          self.set(y, x2, self.at(x2, y2))
          self.set(x2, y2, self.at(y2, x))
          self.set(y2, x, tmp)
        elif quarter_turns == -1:
          self.set(x, y, self.at(y2, x))
          self.set(y2, x, self.at(x2, y2))
          self.set(x2, y2, self.at(y, x2))
          self.set(y, x2, tmp)

def subtract_bytes(a, b):
  return (
    (((a & 0xff000000) - (b & 0xff000000)) & 0xff000000) |
    (((a & 0x00ff0000) - (b & 0x00ff0000)) & 0x00ff0000) |
    (((a & 0x0000ff00) - (b & 0x0000ff00)) & 0x0000ff00) |
    (((a & 0x000000ff) - (b & 0x000000ff)) & 0x000000ff)
  )
def alpha_blend(foreground, background):
  back_a = background & 0xff
  if back_a == 0:
    return foreground
  fore_a = foreground & 0xff
  out_a = fore_a + back_a * (0xff - fore_a) // 0xff
  fore_r = ((foreground & 0xff000000) >> 24) & 0xff
  fore_g = ((foreground & 0x00ff0000) >> 16) & 0xff
  fore_b = ((foreground & 0x0000ff00) >>  8) & 0xff
  back_r = ((background & 0xff000000) >> 24) & 0xff
  back_g = ((background & 0x00ff0000) >> 16) & 0xff
  back_b = ((background & 0x0000ff00) >>  8) & 0xff
  out_r = (fore_r * fore_a // 0xff + back_r * back_a * (0xff - fore_a) // 0xff // 0xff) * 0xff // out_a
  out_b = (fore_b * fore_a // 0xff + back_b * back_a * (0xff - fore_a) // 0xff // 0xff) * 0xff // out_a
  out_g = (fore_g * fore_a // 0xff + back_g * back_a * (0xff - fore_a) // 0xff // 0xff) * 0xff // out_a
  return (
    (out_r << 24) |
    (out_g << 16) |
    (out_b <<  8) |
    (out_a <<  0)
  )

class SimplePngError(Exception):
  pass

def read_png(f, verbose=False):
  try:
    first_bytes = f.read(len(magic_number))
  except UnicodeDecodeError:
    # trigger the non-bytes error below
    first_bytes = ""
  if type(first_bytes) != bytes:
    raise SimplePngError("file must be open in binary mode")
  if first_bytes != magic_number:
    raise SimplePngError("not a png image")

  IHDR = read_chunk(f)
  if IHDR.type_code != b"IHDR":
    raise SimplePngError("expected first chunk to be IHDR")
  try:
    width, height, bit_depth, color_type, compression, filter_method, interlaced = struct.unpack(IHDR_fmt, IHDR.body)
  except struct.error:
    raise SimplePngError("malformed IHDR")
  if verbose: print(
      "metadata: {}x{}, color_type: {}, {}-bit, compression: {}, filter_method: {}, interlaced: {}".format(
          width, height, color_type, bit_depth, compression, filter_method, interlaced))
  if width * height == 0:
    raise SimplePngError("image must have > 0 pixels")
  if compression != 0:
    raise SimplePngError("unsupported compression method: {}".format(compression))
  if filter_method != 0:
    raise SimplePngError("unsupported filter method: {}".format(filter_method))

  if (color_type, bit_depth) == (0, 1):
    bits_per_pixel = 1
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return (
        0xffffff00 * (
          (idat_data[scanline_start + bit_index // 8] >> (7 - (bit_index & 7))) & 0x1
        )
      ) | 0xff
  elif (color_type, bit_depth) == (0, 2):
    bits_per_pixel = 2
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return (
        0x55555500 * (
          (idat_data[scanline_start + bit_index // 8] >> (6 - (bit_index & 6))) & 0x3
        )
      ) | 0xff
  elif (color_type, bit_depth) == (0, 4):
    bits_per_pixel = 4
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return (
        0x11111100 * (
          (idat_data[scanline_start + bit_index // 8] >> (4 - (bit_index & 4))) & 0xf
        )
      ) | 0xff
  elif (color_type, bit_depth) == (0, 8):
    bits_per_pixel = 8
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return (
        0x01010100 * idat_data[scanline_start + bit_index // 8]
      ) | 0xff
  elif (color_type, bit_depth) == (0, 16):
    bits_per_pixel = 16
    filter_left_delta = 2
    def read_color(idat_data, scanline_start, bit_index):
      return (
        0x01010100 * idat_data[scanline_start + bit_index // 8]
      ) | 0xff
  elif (color_type, bit_depth) == (2, 8):
    bits_per_pixel = 24
    filter_left_delta = 3
    def read_color(idat_data, scanline_start, bit_index):
      return (
        idat_data[scanline_start + bit_index // 8] << 24
      ) | (
        idat_data[scanline_start + bit_index // 8 + 1] << 16
      ) | (
        idat_data[scanline_start + bit_index // 8 + 2] << 8
      ) | 0xff
  elif (color_type, bit_depth) == (2, 16):
    bits_per_pixel = 48
    filter_left_delta = 6
    def read_color(idat_data, scanline_start, bit_index):
      return (
        idat_data[scanline_start + bit_index // 8] << 24
      ) | (
        idat_data[scanline_start + bit_index // 8 + 2] << 16
      ) | (
        idat_data[scanline_start + bit_index // 8 + 4] << 8
      ) | 0xff
  elif (color_type, bit_depth) == (3, 1):
    bits_per_pixel = 1
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return (idat_data[scanline_start + bit_index // 8] >> (7 - (bit_index & 7))) & 0x1
  elif (color_type, bit_depth) == (3, 2):
    bits_per_pixel = 2
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return (idat_data[scanline_start + bit_index // 8] >> (6 - (bit_index & 6))) & 0x3
  elif (color_type, bit_depth) == (3, 4):
    bits_per_pixel = 4
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return (idat_data[scanline_start + bit_index // 8] >> (4 - (bit_index & 4))) & 0xf
  elif (color_type, bit_depth) == (3, 8):
    bits_per_pixel = 8
    filter_left_delta = 1
    def read_color(idat_data, scanline_start, bit_index):
      return idat_data[scanline_start + bit_index // 8]
  elif (color_type, bit_depth) == (4, 8):
    bits_per_pixel = 16
    filter_left_delta = 2
    def read_color(idat_data, scanline_start, bit_index):
      return (
        0x01010100 * idat_data[scanline_start + bit_index // 8]
      ) | (
        idat_data[scanline_start + bit_index // 8 + 1]
      )
  elif (color_type, bit_depth) == (4, 16):
    bits_per_pixel = 32
    filter_left_delta = 4
    def read_color(idat_data, scanline_start, bit_index):
      return (
        0x01010100 * idat_data[scanline_start + bit_index // 8]
      ) | (
        idat_data[scanline_start + bit_index // 8 + 2]
      )
  elif (color_type, bit_depth) == (6, 8):
    bits_per_pixel = 32
    filter_left_delta = 4
    def read_color(idat_data, scanline_start, bit_index):
      return (
        idat_data[scanline_start + bit_index // 8] << 24
      ) | (
        idat_data[scanline_start + bit_index // 8 + 1] << 16
      ) | (
        idat_data[scanline_start + bit_index // 8 + 2] << 8
      ) | (
        idat_data[scanline_start + bit_index // 8 + 3]
      )
  elif (color_type, bit_depth) == (6, 16):
    bits_per_pixel = 64
    filter_left_delta = 8
    def read_color(idat_data, scanline_start, bit_index):
      return (
        idat_data[scanline_start + bit_index // 8] << 24
      ) | (
        idat_data[scanline_start + bit_index // 8 + 2] << 16
      ) | (
        idat_data[scanline_start + bit_index // 8 + 4] << 8
      ) | (
        idat_data[scanline_start + bit_index // 8 + 6]
      )
  else:
    raise SimplePngError("unsupported color type/bit depth combination: {}/{}".format(color_type, bit_depth))

  if interlaced == 0:
    interlacing = no_interlacing
  elif interlaced == 1:
    interlacing = adam7_interlacing
  else:
    raise SimplePngError("unsupported interlace method: {}".format(interlaced))

  pixel_sizes = [(
    (width  + x_scale - x_offset - 1) // x_scale,
    (height + y_scale - y_offset - 1) // y_scale,
  ) for (x_scale, x_offset, y_scale, y_offset) in interlacing]
  # make sure all pixels are accounted for
  assert width * height == sum(w * h for (w, h) in pixel_sizes)

  scanline_lengths = [
    # filter types are present only for >0 width subimages
    int(bool(w)) + (w * bits_per_pixel + 7) // 8
    for (w, _) in pixel_sizes
  ]
  expected_idat_data_len = sum(scanline_length * h for (scanline_length, (_, h)) in zip(scanline_lengths, pixel_sizes))

  # read all the chunks we care about
  idat_accumulator = []
  decompressor = zlib.decompressobj()
  palette = None
  while True:
    chunk = read_chunk(f)
    if chunk.type_code == b"IEND":
      if len(f.read(1)) != 0:
        raise SimplePngError("expected EOF")
      break
    elif chunk.type_code == b"PLTE":
      if color_type & color_type_mask_INDEXED:
        if len(chunk.body) == 0:
          raise SimplePngError("empty PLTE chunk")
        if len(chunk.body) % 3 != 0:
          raise SimplePngError("PLTE chunk length must be a multiple of 3")
        palette = [struct.unpack("!I", bytes(rgb + (0xff,)))[0] for rgb in zip(*[iter(chunk.body)]*3)]
      else:
        if verbose: print("WARNING: ignoring PLTE chunk. color_type {} does not require a palette".format(color_type))
    elif chunk.type_code == b"IDAT":
      if (color_type & color_type_mask_INDEXED) and palette == None:
        raise SimplePngError("missing PLTE chunk")
      idat_accumulator.append(decompressor.decompress(chunk.body))
    else:
      if verbose: print("WARNING: ignoring chunk: " + repr(chunk.type_code))
  idat_accumulator.append(decompressor.flush())
  idat_data = list(b"".join(idat_accumulator))
  if len(idat_data) != expected_idat_data_len:
    raise SimplePngError("unexpected decoded IDAT data length. expected: {}. got: {}".format(expected_idat_data_len, len(idat_data)))

  image = ImageBuffer(width, height)
  data = image.data

  if verbose: filter_type_histogram = collections.Counter()
  in_cursor = 0
  out_cursor = 0
  for pass_index in range(len(interlacing)):
    x_scale, x_offset, y_scale, y_offset = interlacing[pass_index]
    pass_width, pass_height = pixel_sizes[pass_index]
    scanline_length = scanline_lengths[pass_index]
    scanline_content_length = scanline_length - 1
    if pass_width == 0: continue

    for y in range(pass_height):
      filter_type = idat_data[in_cursor]
      in_cursor += 1
      if verbose: filter_type_histogram.update([filter_type])

      # apply filter to the scanline
      if filter_type == 0: # none
        pass
      elif filter_type == 1: # sub
        for i in range(filter_left_delta, scanline_content_length):
          idat_data[in_cursor + i] = (
            idat_data[in_cursor + i] +
            idat_data[in_cursor + i - filter_left_delta]
          ) & 0xff
      elif filter_type == 2: # up
        if y == 0:
          pass
        else:
          for i in range(0, scanline_content_length):
            idat_data[in_cursor + i] = (
              idat_data[in_cursor + i] +
              idat_data[in_cursor - scanline_length + i]
            ) & 0xff
      elif filter_type == 3: # average
        if y == 0:
          for i in range(filter_left_delta, scanline_content_length):
            idat_data[in_cursor + i] = (
              idat_data[in_cursor + i] +
              (idat_data[in_cursor + i - filter_left_delta] >> 1)
            ) & 0xff
        else:
          for i in range(0, filter_left_delta):
            idat_data[in_cursor + i] = (
              idat_data[in_cursor + i] +
              (idat_data[in_cursor - scanline_length + i] >> 1)
            ) & 0xff
          for i in range(filter_left_delta, scanline_content_length):
            idat_data[in_cursor + i] = (
              idat_data[in_cursor + i] + ((
                idat_data[in_cursor + i - filter_left_delta] +
                idat_data[in_cursor - scanline_length + i]
              ) >> 1)
            ) & 0xff
      elif filter_type == 4: # paeth
        if y == 0:
          for i in range(filter_left_delta, scanline_content_length):
            idat_data[in_cursor + i] = (
              idat_data[in_cursor + i] +
              get_paeth_predictor(
                idat_data[in_cursor + i - filter_left_delta],
                0,
                0,
              )
            ) & 0xff
        else:
          for i in range(0, filter_left_delta):
            idat_data[in_cursor + i] = (
              idat_data[in_cursor + i] +
              get_paeth_predictor(
                0,
                idat_data[in_cursor - scanline_length + i],
                0,
              )
            ) & 0xff
          for i in range(filter_left_delta, scanline_content_length):
            idat_data[in_cursor + i] = (
              idat_data[in_cursor + i] +
              get_paeth_predictor(
                idat_data[in_cursor + i - filter_left_delta],
                idat_data[in_cursor - scanline_length + i],
                idat_data[in_cursor - scanline_length + i - filter_left_delta],
              )
            ) & 0xff
      else:
        raise SimplePngError("unrecognized filter type: {}".format(filter_type))

      # now we can read the pixel colors from the bytes
      bit_index = 0
      for x in range(pass_width):
        value = read_color(idat_data, in_cursor, bit_index)
        bit_index += bits_per_pixel
        if palette != None:
          try:
            value = palette[value]
          except IndexError:
            raise SimplePngError("color index out of bounds: {} >= {}".format(value, len(palette)))
        if interlaced == 0:
          data[out_cursor] = value
          out_cursor += 1
        else:
          data[(y * y_scale + y_offset) * width + x * x_scale + x_offset] = value

      in_cursor += scanline_content_length

  if verbose: print("filter types used: " + "   ".join("{}:{}".format(*x) for x in sorted(filter_type_histogram.items())))

  return image

no_interlacing = [
  (1, 0, 1, 0),
]
adam7_interlacing = [
  # (x_scale, x_offset, y_scale, y_offset),
  (8, 0, 8, 0),
  (8, 4, 8, 0),
  (4, 0, 8, 4),
  (4, 2, 4, 0),
  (2, 0, 4, 2),
  (2, 1, 2, 0),
  (1, 0, 2, 1),
]

def get_paeth_predictor(a, b, c):
  p = a + b - c
  pa = abs(p - a)
  pb = abs(p - b)
  pc = abs(p - c)
  if pa <= pb and pa <= pc: return a
  if pb <= pc: return b
  return c

if __name__ == "__main__":
  print("reading base...")
  with open(sys.argv[1], "rb") as f:
    image1 = read_png(f, verbose=True)
  for arg in sys.argv[2:-1]:
    print("reading {}...".format(arg))
    with open(arg, "rb") as f:
      image2 = read_png(f, verbose=True)
    print("compositing...")
    image1.paste(image2, 0, 0, 0, 0)
  if len(sys.argv) >= 3:
    print("writing...")
    with open(sys.argv[-1], "wb") as f:
      write_png(f, image1)
  print("done")

