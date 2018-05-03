# Json Fields

Plotting styles and default graphic options used at CINECA and ARPAE-SIMC
to produce forecast maps

## Directory content

 * `mm_fields.json` contains associations between grib products (the `cfVarName`
 key) and the corrisponding magics function and options.
 * `mm_italy.json` and `mm_emro.json` contains `mcoast` settings and others area-related defaults
 * `plot_grib.py` is a draft script to test the plots


## plot_grib.py

The script requires `Magics` and `gribapi` python modules


Run `python plot_grib.py -h` for help:
```
usage: plot_grib.py [-h] [-j JSON_FIELDS] [-c JSON_COASTS] [-l LEVEL]
                    prod file.grib /out/path/

Plot maps from grib file.

positional arguments:
  prod                  product to be plotted (cfVarName grib key)
  file.grib             file containing data to be plotted
  /out/path/            output dir for plot files

optional arguments:
  -h, --help            show this help message and exit
  -j JSON_FIELDS, --json_fields JSON_FIELDS
                        path to json files with fields options (default:
                        ./mm_fields.json)
  -c JSON_COASTS, --json_coasts JSON_COASTS
                        path to json files with area options (default:
                        ./mm_italy.json)
  -l LEVEL, --level LEVEL
                        level to be plotted (if different from the product
                        default)
```


The output at the moment is one png file for product / endstep, e.g.:
```
tp+00.png
tp+03.png
tp+06.png
```
