//Create a simple operation block.
function [x, y, typ]= operation(job, arg1, arg2)
    x=[];y=[];typ=[];
    blkname = 'operation';
    op = 'and';
    select job
      case 'set' then
        x=arg1;
        graphics = arg1.graphics;
        exprs = graphics.exprs;
        model = arg1.model;
        //[io_group, custom_io_group, io_dir, d_type, d_bw, d_bp, gpio_bi, sample_period] = create_gpio();
        txt = [ 'Block Name (any string)';...
                'OP';];
        [ok, blkname, op exprs] = scicos_getvalue("Set edge detect block parameters",...
                          txt,...
                          list("str", 1, "str", 1),...
                          exprs);
        if ok then
            graphics.out_label = ['out'];
            graphics.in_label = ['in0', 'in1'];
            graphics.style = 'shape=rectangle;fillColor=green';
            //graphics.id = '<p style=""margin-top: 0"">      my edge detect     </p>';
            graphics.exprs = exprs;
            x.graphics = graphics;
            model.in = [1,2];
            model.in2 = [1,1];
            model.out = [1];
            model.out2 = [1];
            x.model = model;
        end
      case 'define' then
        model = scicos_model();
        model.sim = list('munge',4);
        model.blocktype = 'c';
        // Type : column vector of real numbers.
        model.rpar = [0, 3];
        // TODO: do we have to set in2??
        model.in = [1,2];
        model.in2 = [1,1];
        model.out = [1];
        model.out2 = [1];
        // Type : column vector of strings.
        exprs = ['operation'; 'and'];
        gr_i = [];
        // model.label doubles as the on-diagram display text (Scicos
        // aliases it with graphics.id); category is derived separately
        // by get_block_type.sci via file-probe, so this is free to be
        // the block's own name.
        model.label = blkname;
        x=standard_define([3 3],model,exprs,gr_i)
        x.graphics.out_label = ['out'];
        x.graphics.in_label = ['in0', 'in1'];
        x.graphics.style = 'shape=rectangle;fillColor=green';
        //x.graphics.id = '<p style=""margin-top: 0"">      my edge detect     </p>';
        debug_info('operation block loaded...')
    end
  endfunction
  
  
  