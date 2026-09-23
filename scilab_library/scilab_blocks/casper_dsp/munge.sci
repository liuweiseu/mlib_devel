//Create a simple custom block.
function [x, y, typ]= munge(job, arg1, arg2)
    x=[];y=[];typ=[];
    blkname = 'munge';
    total_bits = 128;
    divisions = 4;
    size_bits = 32;
    packing_order = '{3, 2, 1, 0}';
    select job
      case 'set' then
        x=arg1;
        graphics = arg1.graphics;
        exprs = graphics.exprs;
        model = arg1.model;
        //[io_group, custom_io_group, io_dir, d_type, d_bw, d_bp, gpio_bi, sample_period] = create_gpio();
        txt = [ 'Block Name (any string)';...
                'Total Bits';...
                'Divisions';...
                'Size Bits';...
                'Packing Order';];
        [ok, blkname, total_bits, divisions, size_bits, packing_order, exprs] = scicos_getvalue("Set edge detect block parameters",...
                          txt,...
                          list("str", 1, "str", 1, "str",1 , "str",1, "str",1),...
                          exprs);
        if ok then
            total_bits = strtod(total_bits);
            graphics.out_label = ['out'];
            graphics.in_label = ['in'];
            graphics.style = 'shape=rectangle;fillColor=green';
            //graphics.id = '<p style=""margin-top: 0"">      my edge detect     </p>';
            graphics.exprs = exprs;
            x.graphics = graphics;
            model.in = [1];
            model.in2 = [total_bits];
            model.out = [1];
            model.out2 = [total_bits];
            x.model = model;
        end
      case 'define' then
        model = scicos_model();
        model.sim = list('munge',4);
        model.blocktype = 'c';
        // Type : column vector of real numbers.
        model.rpar = [0, 3, 4, 5, 6];
        // TODO: do we have to set in2??
        model.in = [1];
        model.in2 = [128];
        model.out = [1];
        model.out2 = [128];
        // Type : column vector of strings.
        exprs = ['munge'; '128'; '4'; '32'; '{3, 2, 1, 0}'];
        gr_i = [];
        // model.label doubles as the on-diagram display text (Scicos
        // aliases it with graphics.id); category is derived separately
        // by get_block_type.sci via file-probe, so this is free to be
        // the block's own name.
        model.label = blkname;
        x=standard_define([3 3],model,exprs,gr_i)
        x.graphics.out_label = ['out'];
        x.graphics.in_label = ['in'];
        x.graphics.style = 'shape=rectangle;fillColor=green';
        //x.graphics.id = '<p style=""margin-top: 0"">      my edge detect     </p>';
        debug_info('munge block loaded...')
    end
  endfunction
  
  
  