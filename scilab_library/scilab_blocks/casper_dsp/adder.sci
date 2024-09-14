//Create a simple custom block.
function [x, y, typ]= adder(job, arg1, arg2)
  x=[];y=[];typ=[];
  blkname = 'adder';
  a_bitwidth = 0;
  b_bitwidth = 0;
  c_bitwidth = 0;
  select job
    case 'set' then
      x=arg1;
      graphics = arg1.graphics;
      exprs = graphics.exprs;
      model = arg1.model;
      //[io_group, custom_io_group, io_dir, d_type, d_bw, d_bp, gpio_bi, sample_period] = create_gpio();
      txt = [ 'Block Name (any string)';...
              'Input bit width(a)';...
              'Input bit width(b)'; ...
              'Output bit width(c)';];
      [ok, blkname, a_bitwidth, b_bitwidth, c_bitwidth, exprs] = scicos_getvalue("Set adder block parameters",...
                        txt,...
                        list("str", 1, "str",1 ,"str",1, "str",1),...
                        exprs);
      if ok then
        graphics.exprs = exprs;
        x.graphics = graphics;
        x.model = model;
      end
    case 'define' then
      model = scicos_model();
      model.sim = list('adder',4);
      model.blocktype = 'c';
      // Type : column vector of real numbers.
      model.rpar = [0, 3, 4, 5];
      // TODO: do we have to set in2??
      model.in = [1, 2];
      model.in2 = [];
      model.out = 1;
      model.out2 = [];
      // Type : column vector of strings.
      exprs = ['adder'; '32'; '32'; '32'];
      gr_i = [];
      x=standard_define([2 4],model,exprs,gr_i)
      disp('adder block loaded...')
  end
endfunction


