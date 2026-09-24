// bus_maddsub: Xcos block definition, PyQt6-mask pattern. Hand-written
// (not gen_sci_block.py) -- casper_library's "Bus" family blocks pack
// several sub-signals into one physical port, with widths given as
// MATLAB vector-expression mask params (e.g. n_bits_a = "[8]"), so port
// widths here are computed as sum(vector) via bus_vec_width(), not a
// plain scalar parameter lookup. misci/misco/en/dvalid ports that
// casper_library only includes conditionally (misc=='on'/async=='on')
// are always present here for simplicity -- leave unconnected in Xcos
// if unused.
function [x, y, typ] = bus_maddsub(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
    case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = bus_maddsub_update_ports(x, bconfig);
    case 'define' then
        tag = 'bus_maddsub';
        model = scicos_model();
        model.sim = list(tag, 4);
        model.blocktype = 'c';
        model.rpar = [];
        exprs = [];
        gr_i = [];
        model.in = [1, 2, 3, 4];
        model.in2 = [8, 8, 8, 1];
        model.out = [1, 2];
        model.out2 = [8, 1];
        model.label = tag;
        x=standard_define([10.8 10.8],model,exprs,gr_i)
        x.graphics.in_label = ['a', 'b', 'c', 'en'];
        x.graphics.out_label = ['dout', 'dvalid'];
        x.graphics.style = 'shape=rectangle;fillColor=#90EE90';
        x = init_exprs(x);
        debug_info('bus_maddsub block loaded...')
    end
endfunction

function [x] = bus_maddsub_update_ports(obj, bconfigfn)
    x = obj;
    bconfig = fromJSON(bconfigfn, 'file');
    p = bconfig('parameters');
    graphics = x.graphics;
    model = x.model;
    model.in = [1, 2, 3, 4];
    model.in2 = [bus_vec_width(p('n_bits_a')), bus_vec_width(p('n_bits_b')), bus_vec_width(p('n_bits_c')), 1];
    model.out = [1, 2];
    model.out2 = [bus_vec_width(p('n_bits_out')), 1];
    graphics.in_label = ['a', 'b', 'c', 'en'];
    graphics.out_label = ['dout', 'dvalid'];
    graphics.style = 'shape=rectangle;fillColor=#90EE90';
    x.graphics = graphics;
    x.model = model;
endfunction
