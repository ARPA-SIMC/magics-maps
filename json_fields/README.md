# Json Fields

Plotting styles and default graphic options used at CINECA and ARPAE-SIMC
to produce forecast maps

## Directory content

 * `mm_fields.json` contains associations between grib products (the `cfVarName`
 key) and the corrisponding magics function and options.
 * `mm_italy.json` contains `mcoast` settings and others area-realated defaults
 * `plot_grib.py` is a draft script to test the plots (requires `Magics` and
 `gribapi` python modules, run `python plot_grib.py -h` for help)
