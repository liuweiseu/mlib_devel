//Create a simple custom block.
function [x, y, typ]= wbfft(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
    case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = wbfft_update_ports(x, bconfig);
    case 'define' then
        btype = 'dsp';
        tag = 'wbfft';
        model = scicos_model();
        model.sim = list(tag,4);
        model.blocktype = 'c';
        model.rpar = [];
        exprs = [];
        gr_i = [];
        [iports_index, iports_label] = wbfft_create_iports(1);
        model.in = iports_index;
        model.in2 = [1, 1, 7, 16, 16];
        [oports_index, oports_label] = wbfft_create_oports(1);
        model.out = oports_index;
        model.out2 = [1, 1, 7, 18, 18];
        model.label = btype;
        x=standard_define([14 14],model,exprs,gr_i)
        x.graphics.in_label = iports_label;
        x.graphics.out_label = oports_label;
        x.graphics.style = 'shape=rectangle;fillColor=green';
        /* init exprs */
        x = init_exprs(x);
        debug_info('wbfft loaded...')
    end
endfunction

// create input ports index and labels
function [ports_index, ports_label] = wbfft_create_iports(wb_factor)
    ports_label = ['in_sync', 'in_valid', 'in_shiftreg'];
    ports_index = [1, 2, 3];
    for i = 1:wb_factor
        ports_label = [ports_label, 'in_re' + string(i - 1)];
        ports_index = [ports_index, 2*i + 2];
        ports_label = [ports_label, 'in_im' + string(i - 1)];
        ports_index = [ports_index, 2*i + 3];
    end
endfunction

// create output ports index and labels
function [ports_index, ports_label] = wbfft_create_oports(wb_factor)
    ports_label = ['out_sync', 'out_valid', 'out_ovflw'];
    ports_index = [1, 2, 3];
    for i = 1:wb_factor
        ports_label = [ports_label, 'out_re' + string(i - 1)];
        ports_index = [ports_index, 2*i + 2];
        ports_label = [ports_label, 'out_im' + string(i - 1)];
        ports_index = [ports_index, 2*i + 3];
    end
endfunction

function [x]= wbfft_update_ports(arg1, bconfigfn)
    x=arg1;
    bconfig = fromJSON(bconfigfn, 'file');
    graphics = arg1.graphics;
    exprs = graphics.exprs;
    model = arg1.model;
    wb_factor = strtod(bconfig('parameters')('wb_factor'));
    in_dat_w = strtod(bconfig('parameters')('in_dat_w'));
    out_dat_w = strtod(bconfig('parameters')('out_dat_w'));
    nof_points = strtod(bconfig('parameters')('nof_points'));
    evtin = [];
    evtout = [];
    [iports_index, iports_label] = wbfft_create_iports(wb_factor);
    [oports_index, oports_label] = wbfft_create_oports(wb_factor);
    // it seems like we don't care about the io type here.
    io_in = [iports_index;iports_index];
    io_out = [oports_index;oports_index];
    io_in_type = ones(1, length(iports_index));
    io_out_type = ones(1, length(oports_index));
    [model,graphics,ok] = set_io(model, graphics, list(io_in', io_in_type), list(io_out', io_out_type), evtin, evtout);
    model.in = iports_index;
    model.in2 = [1, 1, 1*log2(nof_points), 1*in_dat_w*ones(1, 2*wb_factor)];
    model.out = oports_index;
    model.out2 = [1, 1, 1*log2(nof_points), 1*out_dat_w*ones(1, 2*wb_factor)];
    graphics.in_label = iports_label;
    graphics.out_label = oports_label;
    graphics.style = 'shape=rectangle;fillColor=green'
    graphics.exprs = exprs;
    x.graphics = graphics;
    x.model = model;
endfunction

  
  
  