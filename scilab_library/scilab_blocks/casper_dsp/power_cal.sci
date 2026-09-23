//Create a simple custom block.
function [x, y, typ]= power_cal(job, arg1, arg2)
  x=[];y=[];typ=[];
  blkname = 'power_cal';
  bitwidth = 0;
  select job
    case 'set' then
      x=arg1;
      graphics = arg1.graphics;
      exprs = graphics.exprs;
      model = arg1.model;
      txt = [ 'Block Name (any string)';...
              'Bit Width';];
      [ok, blkname, bitwidth, exprs] = scicos_getvalue("Set Power Cal block parameters",...
                        txt,...
                        list("str", 1, "str",1 ),...
                        exprs);
      if ok then
        // convert string to decimal
        in_port_width = strtod(bitwidth);
        out_port_width = 2 * in_port_width + 1;
        graphics.exprs = exprs;
        graphics.style = 'shape=rectangle;fillColor=green'
        graphics.in_label = ['re', 'im'];
        graphics.out_label = ['pwr'];
        model.in = [1, 2];
        model.in2 = [in_port_width, in_port_width];
        model.out = 1;
        model.out2 = [out_port_width];
        x.model = model;
        x.graphics = graphics;
      end
    case 'define' then
      model = scicos_model();
      model.sim = list('power_cal',4);
      model.blocktype = 'c';
      // Type : column vector of real numbers.
      model.rpar = [0, 3];
      // TODO: do we have to set in2??
      model.in = [1, 2];
      model.in2 = [16, 16];
      model.out = 1;
      model.out2 = [33];
      // Type : column vector of strings.
      exprs = ['power_cal'; '16'];
      gr_i = [];
      // model.label doubles as the on-diagram display text (Scicos
      // aliases it with graphics.id); category is derived separately
      // by get_block_type.sci via file-probe, so this is free to be
      // the block's own name.
      model.label = blkname;
      x=standard_define([4 4],model,exprs,gr_i)
      x.graphics.style = 'shape=rectangle;fillColor=green';
      x.graphics.in_label = ['re', 'im'];
      x.graphics.out_label = ['pwr'];
      debug_info('power cal block loaded...')
  end
endfunction


