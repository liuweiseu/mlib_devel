// stopwatch: Xcos block definition, PyQt6-mask pattern.
// Port list confirmed against the real casper_library_misc.slx standalone
// model (SID 272, Ports=[3,1]): its own top-level Inport/Outport blocks
// (system_272.xml) are start/stop/reset in, count_out out -- NOT the
// best-effort [start,stop]->[count] guess this file previously had
// (missing the reset input entirely). The mask has no parameters at all
// (a bare description block), so count_out's existing count_width-driven
// width is kept as-is; reset is a 1-bit strobe, matching start/stop.
function [x, y, typ] = stopwatch(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
    case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = stopwatch_update_ports(x, bconfig);
    case 'define' then
        tag = 'stopwatch';
        model = scicos_model();
        model.sim = list(tag, 4);
        model.blocktype = 'c';
        model.rpar = [];
        exprs = [];
        gr_i = [];
        model.in = [1, 2, 3];
        model.in2 = [1, 1, 1];
        model.out = [1];
        model.out2 = [32];
        // model.label doubles as the on-diagram display text (Scicos
        // aliases it with graphics.id); category is derived separately by
        // get_block_type.sci via file-probe, so this is free to be the name.
        model.label = tag;
        x=standard_define([8.4 6],model,exprs,gr_i)
        x.graphics.in_label = ['start', 'stop', 'reset'];
        x.graphics.out_label = ['count_out'];
        x.graphics.style = 'shape=rectangle;fillColor=#90EE90';
        /* init exprs */
        x = init_exprs(x);
        debug_info('stopwatch block loaded...')
    end
endfunction

function [x] = stopwatch_update_ports(obj, bconfigfn)
    // fixed port count: only widths/labels change, no set_io() needed
    // (same approach as swreg_update_ports)
    x = obj;
    bconfig = fromJSON(bconfigfn, 'file');
    p = bconfig('parameters');
    graphics = x.graphics;
    model = x.model;
    model.in = [1, 2, 3];
    model.in2 = [1, 1, 1];
    model.out = [1];
    model.out2 = [strtod(p('count_width'))];
    graphics.in_label = ['start', 'stop', 'reset'];
    graphics.out_label = ['count_out'];
    graphics.style = 'shape=rectangle;fillColor=#90EE90';
    x.graphics = graphics;
    x.model = model;
endfunction
