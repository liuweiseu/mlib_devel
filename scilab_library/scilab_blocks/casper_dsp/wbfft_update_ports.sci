function [x]= wbfft_update_ports(arg1, bconfigfn)
    x=[];
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
