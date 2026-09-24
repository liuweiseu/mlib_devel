// ten_gbe: Xcos block definition, PyQt6-mask pattern. Hand-written
// (not gen_sci_block.py) -- port list confirmed against the real
// xps_library/xps_models/IO/ten_gbe.slx standalone model's own top-level
// Inport/Outport blocks (names + the block's own "Ports" attribute, which
// matches this count exactly), NOT a best-effort guess.
function [x, y, typ] = ten_gbe(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
    case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = ten_gbe_update_ports(x, bconfig);
    case 'define' then
        tag = 'ten_gbe';
        model = scicos_model();
        model.sim = list(tag, 4);
        model.blocktype = 'c';
        model.rpar = [];
        exprs = [];
        gr_i = [];
        model.in = [1, 2, 3, 4, 5, 6, 7, 8];
        model.in2 = [1, 64, 1, 32, 16, 1, 1, 1];
        model.out = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
        model.out2 = [1, 1, 1, 1, 1, 64, 1, 32, 16, 1, 1, 1];
        model.label = tag;
        x=standard_define([9 18],model,exprs,gr_i)
        x.graphics.in_label = ['rst', 'tx_data', 'tx_valid', 'tx_dest_ip', 'tx_dest_port', 'tx_end_of_frame', 'rx_ack', 'rx_overrun_ack'];
        x.graphics.out_label = ['led_up', 'led_rx', 'led_tx', 'tx_afull', 'tx_overflow', 'rx_data', 'rx_valid', 'rx_source_ip', 'rx_source_port', 'rx_end_of_frame', 'rx_bad_frame', 'rx_overrun'];
        x.graphics.style = 'shape=rectangle;fillColor=yellow';
        x = init_exprs(x);
        debug_info('ten_gbe block loaded...')
    end
endfunction

function [x] = ten_gbe_update_ports(obj, bconfigfn)
    x = obj;
    bconfig = fromJSON(bconfigfn, 'file');
    p = bconfig('parameters');
    graphics = x.graphics;
    model = x.model;
    model.in = [1, 2, 3, 4, 5, 6, 7, 8];
    model.in2 = [1, 64, 1, 32, 16, 1, 1, 1];
    model.out = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    model.out2 = [1, 1, 1, 1, 1, 64, 1, 32, 16, 1, 1, 1];
    graphics.in_label = ['rst', 'tx_data', 'tx_valid', 'tx_dest_ip', 'tx_dest_port', 'tx_end_of_frame', 'rx_ack', 'rx_overrun_ack'];
    graphics.out_label = ['led_up', 'led_rx', 'led_tx', 'tx_afull', 'tx_overflow', 'rx_data', 'rx_valid', 'rx_source_ip', 'rx_source_port', 'rx_end_of_frame', 'rx_bad_frame', 'rx_overrun'];
    graphics.style = 'shape=rectangle;fillColor=yellow';
    x.graphics = graphics;
    x.model = model;
endfunction
