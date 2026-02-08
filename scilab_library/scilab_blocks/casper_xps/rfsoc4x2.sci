//Create a simple custom block.
function [x, y, typ]= rfsoc4x2(job, arg1, arg2)
  x=[];y=[];typ=[];
  blkname = 'RFSoC4x2';
  hd_plat = -1;
  fabric_clk_src = -1;
  fabric_clk_rate = -1;
  pll_clk_rate = -1;
  sample_period = -1;
  select job
    case 'set' then
      x=arg1;
      graphics = arg1.graphics;
      exprs = graphics.exprs;
      model = arg1.model;
      txt = [ 'Block Name (any string)';...
              'Hardware Platform';...
              'User IP Clock source'; ...
              'User IP Clock Rate(MHz)';...
              'RFPLL PL Clock Rate(MHz)';...
              'Sample Period'];
      // get args from gui
      [ok, blkname, hd_plat, fabric_clk_src, fabric_clk_rate, pll_clk_rate, sample_period, exprs] = scicos_getvalue("Set RFSoC4x2 block parameters",...
                        txt,...
                        list("str", 1, "str", 1 ,"str",1,"str",1,"str",1,"str",1),...
                        exprs);
      if ok then
        // as rpar has to be a float vector, we need to convert the string to float
        // if hd_plat == 'rfsoc4x2:xczu48dr' then
        //   hd_plat_r = 0;
        // end
        // if fabric_clk_src == 'adc_clk' then
        //   fabric_clk_src_r = 0;
        // end
        // generate rpar
        // rpar = [hd_plat_r, fabric_clk_src_r, fabric_clk_rate, pll_clk_rate, sample_period];
        // update model
        // model.rpar = rpar;
        graphics.exprs = exprs;
        x.graphics = graphics;
        x.model = model;
      end
    case 'define' then
        /* the block init code is here */
        btype = 'xps';
        tag = 'rfsoc4x2';
        /* create model data structure */
        /* 1. fixed part */
        model = scicos_model();
        model.sim = list(tag,4);
        model.blocktype = 'c';
        model.label = btype;
        model.rpar = [];
        /* create the block data structure */
        exprs = [];
        gr_i = [];
        x=standard_define([4 4],model,exprs,gr_i);
        x = init_exprs(x);
        debug_info('rfsoc4x2 block loaded...');
  end
endfunction