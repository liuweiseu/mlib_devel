//Create a simple custom block.
function [x, y, typ]= rfdc(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
      case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = rfdc_update_ports(x, bconfig);
      case 'define' then
        btype = 'xps';
        tag = 'rfdc';
        model = scicos_model();
        model.sim = list('rfdc',4);
        model.blocktype = 'c';
        // Type : column vector of real numbers.
        model.rpar = [0, 5];
        // TODO: do we have to set in2??
        model.in = [1, 2, 3, 4, 5, 6, 7, 8];
        model.in2 = [128, 128, 128, 128, 128, 128, 128, 128];
        model.out = [1, 2, 3, 4, 5, 6, 7, 8];
        model.out2 = [128, 128, 128, 128, 128, 128, 128, 128];
        gr_i = [];
        exprs = [];
        model.label = btype;
        x=standard_define([14 14],model,exprs,gr_i)
        x.graphics.out_label = ['m00_axis_tdata', 'm02_axis_tdata', 'm10_axis_tdata', 'm12_axis_tdata', 'm20_axis_tdata', 'm22_axis_tdata', 'm30_axis_tdata', 'm32_axis_tdata'];
        x.graphics.in_label = ['m00_axis_tdata_sim', 'm02_axis_tdata_sim', 'm10_axis_tdata_sim', 'm12_axis_tdata_sim', 'm20_axis_tdata_sim', 'm22_axis_tdata_sim', 'm30_axis_tdata_sim', 'm32_axis_tdata_sim'];
        x.graphics.style = 'shape=rectangle;fillColor=yellow'
        x = init_exprs(x);
        debug_info('rfdc block loaded...')
    end
  endfunction
  

function [x] = rfdc_update_ports(obj, bconfigfn)
    bconfig = fromJSON(bconfigfn, 'file');
    // TODO: add support for QT
    // check the bconfig file, getting enable info
    Tile224_enable = bconfig('parameters')('Tile224_enable');
    t224_DT_adc0_enable = bconfig('parameters')('t224_DT_adc0_enable');
    t224_DT_adc1_enable = bconfig('parameters')('t224_DT_adc1_enable');
    Tile225_enable = bconfig('parameters')('Tile225_enable');
    t225_DT_adc0_enable = bconfig('parameters')('t225_DT_adc0_enable');
    t225_DT_adc1_enable = bconfig('parameters')('t225_DT_adc1_enable');
    Tile226_enable = bconfig('parameters')('Tile226_enable');
    t226_DT_adc0_enable = bconfig('parameters')('t226_DT_adc0_enable');
    t226_DT_adc1_enable = bconfig('parameters')('t226_DT_adc1_enable');
    Tile227_enable = bconfig('parameters')('Tile227_enable');
    t227_DT_adc0_enable = bconfig('parameters')('t227_DT_adc0_enable');
    t227_DT_adc1_enable = bconfig('parameters')('t227_DT_adc1_enable');
    out_label = [];
    in_label = [];
    in = [];
    in2 = [];
    out = [];
    out2 = [];
    nport = 0;
    // check tile224 status
    if Tile224_enable == 'on' then
        if t224_DT_adc0_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm00_axis_tdata_sim'];
            out_label = [out_label, 'm00_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
        if t224_DT_adc1_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm02_axis_tdata_sim'];
            out_label = [out_label, 'm02_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
    end
    // check tile225 status
    if Tile225_enable == 'on' then
        if t225_DT_adc0_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm10_axis_tdata_sim'];
            out_label = [out_label, 'm10_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
        if t225_DT_adc1_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm12_axis_tdata_sim'];
            out_label = [out_label, 'm12_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
    end
    // check tile226 status
    if Tile226_enable == 'on' then
        if t226_DT_adc0_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm20_axis_tdata_sim'];
            out_label = [out_label, 'm20_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
        if t226_DT_adc1_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm22_axis_tdata_sim'];
            out_label = [out_label, 'm22_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
    end
    // check tile227 status
    if Tile227_enable == 'on' then
        if t227_DT_adc0_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm30_axis_tdata_sim'];
            out_label = [out_label, 'm30_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
        if t227_DT_adc1_enable == 'on' then
            nport = nport + 1;
            in_label = [in_label, 'm32_axis_tdata_sim'];
            out_label = [out_label, 'm32_axis_tdata'];
            in = [in, nport];
            in2 = [in2, 128];
            out = [out, nport];
            out2 = [out2, 128];
        end
    end
    // put the port info to the obj
    x=obj;
    graphics = obj.graphics;
    exprs = graphics.exprs;
    model = obj.model;
    evtin = [];
    evtout = [];
    io_in = [in;in];
    io_out = [out;out];
    io_in_type = ones(1, length(in));
    io_out_type = ones(1, length(out));
    [model,graphics,ok] = set_io(model, graphics, list(io_in', io_in_type), list(io_out', io_out_type), evtin, evtout);
    model.out = out;
    model.out2 = out2;
    model.in = in;
    model.in2 = in2;
    graphics.out_label = out_label;
    graphics.in_label = in_label;
    graphics.style = 'shape=rectangle;fillColor=yellow'
    graphics.exprs = exprs;
    x.graphics = graphics;
    x.model = model;
endfunction