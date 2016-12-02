
import os
import sys
import itertools

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import simplepng

schaik_dir = os.path.join(os.path.dirname(__file__), "deps", "PngSuite-2013jan13")
schaik_basic_names = [
  "basn0g01.png",
  "basn0g02.png",
  "basn0g04.png",
  "basn0g08.png",
  "basn0g16.png",
  "basn2c08.png",
  "basn2c16.png",
  "basn3p01.png",
  "basn3p02.png",
  "basn3p04.png",
  "basn3p08.png",
  "basn4a08.png",
  "basn4a16.png",
  "basn6a08.png",
  "basn6a16.png",
]
schaik_interlaced_names = [
  "basi0g01.png",
  "basi0g02.png",
  "basi0g04.png",
  "basi0g08.png",
  "basi0g16.png",
  "basi2c08.png",
  "basi2c16.png",
  "basi3p01.png",
  "basi3p02.png",
  "basi3p04.png",
  "basi3p08.png",
  "basi4a08.png",
  "basi4a16.png",
  "basi6a08.png",
  "basi6a16.png",
]
schaik_background_names = [
  "bgai4a08.png",
  "bgai4a16.png",
  "bgan6a08.png",
  "bgan6a16.png",
  "bgbn4a08.png",
  "bggn4a16.png",
  "bgwn6a08.png",
  "bgyn6a16.png",
]
schaik_ancillary_ignore_names = [
  "ccwn2c08.png",
  "ccwn3p08.png",
  "cdfn2c08.png",
  "cdhn2c08.png",
  "cdsn2c08.png",
  "cdun2c08.png",
  "ch1n3p04.png",
  "ch2n3p08.png",
  "cm0n0g04.png",
  "cm7n0g04.png",
  "cm9n0g04.png",
  "cs3n2c16.png",
  "cs3n3p08.png",
  "cs5n2c08.png",
  "cs5n3p08.png",
  "cs8n2c08.png",
  "cs8n3p08.png",
  "ct0n0g04.png",
  "ct1n0g04.png",
  "cten0g04.png",
  "ctfn0g04.png",
  "ctgn0g04.png",
  "cthn0g04.png",
  "ctjn0g04.png",
  "ctzn0g04.png",
]
schaik_filter_type_names = [
  "f00n0g08.png",
  "f00n2c08.png",
  "f01n0g08.png",
  "f01n2c08.png",
  "f02n0g08.png",
  "f02n2c08.png",
  "f03n0g08.png",
  "f03n2c08.png",
  "f04n0g08.png",
  "f04n2c08.png",
  "f99n0g04.png",
]
schaik_gamma_ignore_names = [
  "g03n0g16.png",
  "g03n2c08.png",
  "g03n3p04.png",
  "g04n0g16.png",
  "g04n2c08.png",
  "g04n3p04.png",
  "g05n0g16.png",
  "g05n2c08.png",
  "g05n3p04.png",
  "g07n0g16.png",
  "g07n2c08.png",
  "g07n3p04.png",
  "g10n0g16.png",
  "g10n2c08.png",
  "g10n3p04.png",
  "g25n0g16.png",
  "g25n2c08.png",
  "g25n3p04.png",
]
schaik_chunk_ordering_names = [
  "oi1n0g16.png",
  "oi1n2c16.png",
  "oi2n0g16.png",
  "oi2n2c16.png",
  "oi4n0g16.png",
  "oi4n2c16.png",
  "oi9n0g16.png",
  "oi9n2c16.png",
]
schaik_pallet_names = [
  "pp0n2c16.png",
  "pp0n6a08.png",
  "ps1n0g08.png",
  "ps1n2c16.png",
  "ps2n0g08.png",
  "ps2n2c16.png",
]
schaik_odd_size_names = [
  "s01i3p01.png",
  "s01n3p01.png",
  "s02i3p01.png",
  "s02n3p01.png",
  "s03i3p01.png",
  "s03n3p01.png",
  "s04i3p01.png",
  "s04n3p01.png",
  "s05i3p02.png",
  "s05n3p02.png",
  "s06i3p02.png",
  "s06n3p02.png",
  "s07i3p02.png",
  "s07n3p02.png",
  "s08i3p02.png",
  "s08n3p02.png",
  "s09i3p02.png",
  "s09n3p02.png",
  "s32i3p04.png",
  "s32n3p04.png",
  "s33i3p04.png",
  "s33n3p04.png",
  "s34i3p04.png",
  "s34n3p04.png",
  "s35i3p04.png",
  "s35n3p04.png",
  "s36i3p04.png",
  "s36n3p04.png",
  "s37i3p04.png",
  "s37n3p04.png",
  "s38i3p04.png",
  "s38n3p04.png",
  "s39i3p04.png",
  "s39n3p04.png",
  "s40i3p04.png",
  "s40n3p04.png",
]
schaik_transparency_names = [
  "tbbn0g04.png",
  "tbbn2c16.png",
  "tbbn3p08.png",
  "tbgn2c16.png",
  "tbgn3p08.png",
  "tbrn2c08.png",
  "tbwn0g16.png",
  "tbwn3p08.png",
  "tbyn3p08.png",
  "tm3n3p02.png",
  "tp0n0g08.png",
  "tp0n2c08.png",
  "tp0n3p08.png",
  "tp1n3p08.png",
]
schaik_zlib_names = [
  "z00n2c08.png",
  "z03n2c08.png",
  "z06n2c08.png",
  "z09n2c08.png",
]

schaik_error_names = [
  "xc1n0g08.png",
  "xc9n2c08.png",
  "xcrn0g04.png",
  "xcsn0g01.png",
  "xd0n2c08.png",
  "xd3n2c08.png",
  "xd9n2c08.png",
  "xdtn0g01.png",
  "xhdn0g08.png",
  "xlfn0g04.png",
  "xs1n0g01.png",
  "xs2n0g01.png",
  "xs4n0g01.png",
  "xs7n0g01.png",
]

def test_errors():
  def test_error(input_path):
    with open(input_path, "rb") as f:
      try:
        simplepng.read_png(f)
      except simplepng.SimplePngError:
        return
      except:
        assert False, input_path + ": crashed"
      else:
        assert False, input_path + ": expected to throw"
  for name in schaik_error_names:
    test_error(os.path.join(schaik_dir, name))

def test_dont_crash():
  # TODO: make this actually compare pixels to an expected value
  groups = [
    schaik_basic_names,
    schaik_interlaced_names,
    schaik_background_names,
    schaik_ancillary_ignore_names,
    schaik_filter_type_names,
    schaik_gamma_ignore_names,
    schaik_chunk_ordering_names,
    schaik_pallet_names,
    schaik_odd_size_names,
    schaik_transparency_names,
    schaik_zlib_names,
  ]
  for name in itertools.chain(*groups):
    input_path = os.path.join(schaik_dir, name)
    with open(input_path, "rb") as f:
      try:
        simplepng.read_png(f)
      except:
        assert False, input_path + ": crashed"

if __name__ == "__main__":
  test_errors()
  test_dont_crash()
