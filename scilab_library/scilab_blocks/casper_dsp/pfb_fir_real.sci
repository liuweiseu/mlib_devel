// pfb_fir_real: Xcos block definition, PyQt6-mask pattern.
// Hand-written (not gen_sci_block.py) -- like fft_wideband_real, the port
// count scales with TWO mask parameters jointly: MakeBiplex (POLS = 2 iff
// 'on', else 1) and n_inputs (POLS*2^n_inputs real inputs/outputs), which
// the single factor_key "dynamic" generator can't express. Port layout
// mirrors casper_library/pfb_fir_real_init.m's own port names verbatim
// (pol<p>_in<n>/pol<p>_out<n>, 1-indexed) -- confirmed against
// casper_dsp/rtl/PFBs/pfb_fir_real.sv's header comment, which documents the
// exact same port order.
//
// HDL backend: casper_dsp/rtl/PFBs/pfb_fir_real.sv. Several mask parameters
// are declared here (for parameter-list completeness/traceability against
// the original casper_library mask) but not yet functionally implemented by
// the HDL -- see mask.py's validate_config and
// mlib_devel_notes/pfb_fir_real_hdl_plan.md for which ones and why.
function [x, y, typ] = pfb_fir_real(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
    case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = pfb_fir_real_update_ports(x, bconfig);
    case 'define' then
        tag = 'pfb_fir_real';
        model = scicos_model();
        model.sim = list(tag,4);
        model.blocktype = 'c';
        model.rpar = [];
        exprs = [];
        gr_i = [];
        // initial on-canvas shape, before the user ever opens the mask --
        // matches the JSON template's own defaults (n_inputs=1,
        // MakeBiplex=off so pols=1, BitWidthIn=8, BitWidthOut=18)
        default_pols = 1;
        default_n_inputs = 1;
        default_bit_width_in = 8;
        default_bit_width_out = 18;
        [iports_index, iports_label] = pfb_fir_real_create_iports(default_pols, default_n_inputs);
        model.in = iports_index;
        model.in2 = [1, default_bit_width_in*ones(1, default_pols*2^default_n_inputs)];
        [oports_index, oports_label] = pfb_fir_real_create_oports(default_pols, default_n_inputs);
        model.out = oports_index;
        model.out2 = [1, default_bit_width_out*ones(1, default_pols*2^default_n_inputs)];
        model.label = tag;
        x=standard_define([13 15],model,exprs,gr_i)
        x.graphics.in_label = iports_label;
        x.graphics.out_label = oports_label;
        /* init exprs */
        x = init_exprs(x);
        x.graphics.style = pfb_fir_real_build_style(x.graphics.exprs(1));
        debug_info('pfb_fir_real loaded...')
    end
endfunction

// Port layout, fixed part:
//   in:  sync (1), then pol<p>_in<n> for p=1..pols, n=1..2^n_inputs
//   out: sync_out (1), then pol<p>_out<n> for p=1..pols, n=1..2^n_inputs
//
// create input ports index and labels
function [ports_index, ports_label] = pfb_fir_real_create_iports(pols, n_inputs)
    ports_label = ['sync'];
    ports_index = [1];
    port = 2;
    for p = 1:pols
        for n = 1:2^n_inputs
            ports_label = [ports_label, 'pol' + string(p) + '_in' + string(n)];
            ports_index = [ports_index, port];
            port = port + 1;
        end
    end
endfunction

// create output ports index and labels
function [ports_index, ports_label] = pfb_fir_real_create_oports(pols, n_inputs)
    ports_label = ['sync_out'];
    ports_index = [1];
    port = 2;
    for p = 1:pols
        for n = 1:2^n_inputs
            ports_label = [ports_label, 'pol' + string(p) + '_out' + string(n)];
            ports_index = [ports_index, port];
            port = port + 1;
        end
    end
endfunction

// Output bit-width, for Xcos's own port width display / check_bit_width.sci
// cross-checking only -- NOT authoritative. The real formula
// (casper_dsp/rtl/PFBs/pfb_fir_real.sv's N_BITS_OUT) needs BIT_GROWTH, which
// depends on the actual window+sinc coefficient values
// (nextpow2(max sub-filter gain)), not just mask parameters -- that can
// only be computed numerically (by
// rtl/PFBs/scripts/gen_pfb_coeffs.py --bit-width-in), not reimplemented
// here. This function assumes BIT_GROWTH=1 (the Verilog parameter's own
// default) purely so Xcos has *some* width to display; the real HDL
// generation (dsp_blocks/pfb_fir_real.py's modify_top()) computes and uses
// the true value. A real design may see a check_bit_width.sci mismatch
// warning against this approximation -- that is expected, not a bug.
function [w] = pfb_fir_real_out_width(bit_width_in, bit_width_out, coeff_bit_width)
    if bit_width_out <> 0 then
        w = bit_width_out;
    else
        bit_growth_assumed = 1;
        adder_bin_pt_out = bit_width_in + coeff_bit_width - 2;
        w = bit_growth_assumed + 1 + adder_bin_pt_out;
    end
endfunction

function [x]= pfb_fir_real_update_ports(arg1, bconfigfn)
    x=arg1;
    bconfig = fromJSON(bconfigfn, 'file');
    graphics = arg1.graphics;
    exprs = graphics.exprs;
    model = arg1.model;
    params = bconfig('parameters');
    n_inputs = strtod(params('n_inputs'));
    pols = (params('MakeBiplex') == 'on') + 1;
    bit_width_in = strtod(params('BitWidthIn'));
    bit_width_out = strtod(params('BitWidthOut'));
    coeff_bit_width = strtod(params('CoeffBitWidth'));
    out_width = pfb_fir_real_out_width(bit_width_in, bit_width_out, coeff_bit_width);
    evtin = [];
    evtout = [];
    [iports_index, iports_label] = pfb_fir_real_create_iports(pols, n_inputs);
    [oports_index, oports_label] = pfb_fir_real_create_oports(pols, n_inputs);
    io_in = [iports_index;iports_index];
    io_out = [oports_index;oports_index];
    io_in_type = ones(1, length(iports_index));
    io_out_type = ones(1, length(oports_index));
    [model,graphics,ok] = set_io(model, graphics, list(io_in', io_in_type), list(io_out', io_out_type), evtin, evtout);
    model.in = iports_index;
    // sync width 1, then pols*2^n_inputs real input samples at bit_width_in each
    model.in2 = [1, bit_width_in*ones(1, pols*2^n_inputs)];
    model.out = oports_index;
    // sync_out width 1, then pols*2^n_inputs real output samples at out_width each
    model.out2 = [1, out_width*ones(1, pols*2^n_inputs)];
    graphics.in_label = iports_label;
    graphics.out_label = oports_label;
    graphics.style = pfb_fir_real_build_style(params('name'));
    graphics.exprs = exprs;
    x.graphics = graphics;
    x.model = model;
endfunction

/* build the graphics.style string for a given user-configurable block
   name, shown below the fill color (see displayedLabel). Strips ';' and
   '=' from the name since those are the mxGraph style string's own
   delimiter characters. */
function [style] = pfb_fir_real_build_style(name)
    name = strsubst(string(name), ';', '');
    name = strsubst(name, '=', '');
    style = 'shape=rectangle;fillColor=#90EE90;strokeColor=black;fontColor=black;fontSize=12;align=center;verticalAlign=top;verticalLabelPosition=bottom;noLabel=0;displayedLabel=' + name + ';whiteSpace=wrap;html=1;spacing=4;';
endfunction
