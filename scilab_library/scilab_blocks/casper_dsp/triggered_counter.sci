// triggered_counter: Xcos block definition, PyQt6-mask pattern.
// Port list confirmed against the real casper_library_misc.slx standalone
// model (SID 303, Ports=[1,2]): its own top-level Inport/Outport blocks
// (system_303.xml) are trig in, count/valid out -- NOT the best-effort
// [trig]->[count] guess this file previously had (missing the valid
// output entirely). The block has no mask at all, so count's existing
// count_width-driven width is kept as-is; valid is a 1-bit strobe,
// matching every other control/flag port in this library.
function [x, y, typ] = triggered_counter(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
    case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = triggered_counter_update_ports(x, bconfig);
    case 'define' then
        tag = 'triggered_counter';
        model = scicos_model();
        model.sim = list(tag, 4);
        model.blocktype = 'c';
        model.rpar = [];
        exprs = [];
        gr_i = [];
        model.in = [1];
        model.in2 = [1];
        model.out = [1, 2];
        model.out2 = [32, 1];
        // model.label doubles as the on-diagram display text (Scicos
        // aliases it with graphics.id); category is derived separately by
        // get_block_type.sci via file-probe, so this is free to be the name.
        model.label = tag;
        x=standard_define([7 7],model,exprs,gr_i)
        x.graphics.in_label = ['trig'];
        x.graphics.out_label = ['count', 'valid'];
        x.graphics.style = 'shape=rectangle;fillColor=#90EE90';
        /* init exprs */
        x = init_exprs(x);
        debug_info('triggered_counter block loaded...')
    end
endfunction

function [x] = triggered_counter_update_ports(obj, bconfigfn)
    // fixed port count: only widths/labels change, no set_io() needed
    // (same approach as swreg_update_ports)
    x = obj;
    bconfig = fromJSON(bconfigfn, 'file');
    p = bconfig('parameters');
    graphics = x.graphics;
    model = x.model;
    model.in = [1];
    model.in2 = [1];
    model.out = [1, 2];
    model.out2 = [strtod(p('count_width')), 1];
    graphics.in_label = ['trig'];
    graphics.out_label = ['count', 'valid'];
    graphics.style = 'shape=rectangle;fillColor=#90EE90';
    x.graphics = graphics;
    x.model = model;
endfunction
