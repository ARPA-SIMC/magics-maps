# -*- coding: utf-8 -*-

import argparse
import os,sys
import json
import gribapi
import Magics.macro as mm

# biteify  functions only needed for python 2.x
# for issues handling unicode strings in magics binding

def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


def get_grib_metadata(filename, shortname, level=None):
    """Restituisce l'elenco dei grib che fanno match con shortname e level passati"""

    grib_get_or_none = lambda gid, key: gribapi.grib_get(gid, key) if gribapi.grib_is_defined(gid, key) else None
    
    with open(filename) as fp:
        # Itero sui messaggi GRIB
        while True:
            gid = gribapi.grib_new_from_file(fp)
            # when None, there are no more messages
            if gid is None:
                break
            # grib message should have these metadata
            if grib_get_or_none(gid, "cfVarName") != shortname:
                continue
            if level is not None and grib_get_or_none(gid, "level") != level:
                continue

            # custom scaling options
            global scaling_offset
            global scaling_factor

            if grib_get_or_none(gid, "units") == 'K':
                scaling_offset=-273.15

            if grib_get_or_none(gid, "units") == 'm':
                scaling_factor = 0.001

            if grib_get_or_none(gid, "units") == 'pa':
                scaling_factor = 0.01

            yield gid, grib_get_or_none(gid, "endStep")
            

def group_grib_metadata_by_fstep(filename, product, level=None):
    from itertools import groupby

    if product != 'uv':
        return {
            endStep: gid for gid, endStep in get_grib_metadata(filename, product, level)
        }
    else:
        metadata = {}
        for u, endStep in get_grib_metadata(filename, 'u', level):
            metadata[endStep] = [u]
        for v, endStep in get_grib_metadata(filename, 'v', level):
            try:
                metadata[endStep].append(v)
            except:
                raise Exception("u or v missing")
            
        for uv in metadata.values():
            if len(uv) != 2:
                raise Exception("u or v missing")
            
        return metadata


scaling_factor = 1.0
scaling_offset = 0.0
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Plot grib')
    parser = argparse.ArgumentParser(description='Plot maps from grib file.')
    parser.add_argument('-j','--json_fields', default='mm_fields.json',
                        help='path to json files with fields options (default: ./mm_fields.json)')
    parser.add_argument('-c','--json_coasts', default='mm_italy.json',
                        help='path to json files with area options (default: ./mm_italy.json)')
    parser.add_argument('product', metavar='prod', help='product to be plotted (cfVarName grib key)')
    parser.add_argument('-l', '--level',
                        help='level to be plotted (if different from the product default)')
    parser.add_argument('grib', metavar='file.grib', help='file containing data to be plotted')
    parser.add_argument('outdir', metavar='/out/path/', help='output dir for plot files')

    args = parser.parse_args()

    if not os.path.isfile(args.grib):
        sys.stderr.write('grib file specified (' + args.grib + ') is not a file\n\n')
        sys.exit(2)

    if not os.path.isfile(args.json_fields):
        sys.stderr.write('grib file specified (' + args.json_fields + ') is not a file\n\n')
        sys.exit(2)

    if not os.path.isfile(args.json_coasts):
        sys.stderr.write('grib file specified (' + args.json_coasts + ') is not a file\n\n')
        sys.exit(2)
        
    if not os.path.isdir(args.outdir):
        sys.stderr.write('output path specified (' + args.outdir + ') is not a directory\n\n')
        sys.exit(2)

        
    with open(args.json_fields) as json_data:
        # this should/could be set as "json.load" for pyhton3
        mm_fields = json_load_byteified(json_data)

    with open(args.json_coasts) as json_data:
        # this should/could be set as "json.load" for pyhton3
        mm_coasts = json_load_byteified(json_data)

    gb_met = group_grib_metadata_by_fstep(args.grib, args.product, args.level)

    os.environ["MAGPLUS_QUIET"] = "true"
    
    area = mm.mmap(**mm_coasts["mmap"])
    bg = mm.mcoast(**mm_coasts["background"])
    fg = mm.mcoast(**mm_coasts["foreground"])

    #TODO: legend_title_text="<grib_info key='units'/>"
    legend = mm.mlegend(
        legend='on',
        legend_display_type='continuous',
        legend_border='off',
        legend_text_font_size=0.8,
        legend_text_colour="black",
        legend_box_mode ='positional',
        legend_box_x_position=26.,
        legend_box_y_position=1.00,
        legend_box_x_length=2.00,
        legend_box_y_length=16.00,
        legend_title='on',
        legend_title_orientation='horizontal',
        legend_title_position='top',
        legend_title_position_ratio=5.
    )

    
    for k, v in gb_met.iteritems():
        print("processing: " + args.product + " +" + str(k).zfill(2))
        
        input_data = mm.mgrib(
            grib_input_file_name = args.grib,
            grib_field_position = v,
            grib_automatic_scaling = 'off',
            grib_scaling_factor = scaling_factor,
            grib_scaling_offset = scaling_offset,
            grib_automatic_derived_scaling = 'off',
        )

        #TODO: fileout handling
        fileout=str(args.product) + '+' + str(k).zfill(2)
        out = mm.output(
            output_name = args.outdir + "/" + fileout,
            output_formats=['png'],
            output_name_first_page_number = "off",
            output_width = 1280
        )

        title = mm.mtext(
            text_lines  = ["<grib_info key='name'/> -  <grib_info key='valid-date'/>"],
            text_colour = 'black',
            text_font_size = 1.0,
            text_justification = "left",
            text_font_style='bold',
            text_mode = 'positional',
            text_box_X_position = 1.,
            text_box_Y_position = 17.5
        )

        # cleanup json for unwanted parameters
        # (they show up as warnings in Magics output)
        shading_opt = mm_fields[args.product].copy()
        del shading_opt['magic_func']
        del shading_opt['nameECMF']
    
        shading = getattr(mm, mm_fields[args.product]['magic_func'])(**shading_opt)

        mm.plot(out, area, bg, input_data, shading, legend, fg, title)
