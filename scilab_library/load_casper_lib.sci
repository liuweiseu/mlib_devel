loadXcosLibs;

// load the scilab functions
exec('scilab_library/jasper.sci');
exec('scilab_library/jasper_frontend.sci');
exec('scilab_library/scilab_blocks/utils/gen_port_info.sci');
exec('scilab_library/scilab_blocks/utils/gen_port_suffix.sci');
exec('scilab_library/scilab_blocks/utils/get_port_width.sci');
exec('scilab_library/scilab_blocks/utils/search_for_src_blk.sci');
exec('scilab_library/scilab_blocks/utils/check_block_type.sci');

// TODO: load the xps and dsp blocks automatically
// all of the blocks in the scilab_library/casper_xps and 
// scilab_library/casper_dsp directories should be loaded autocaically

// add casper xps blocks
disp('------Loading CASPER XPS...------');
// load the xps blocks
exec('scilab_library/scilab_blocks/casper_xps/rfsoc4x2.sci');
exec('scilab_library/scilab_blocks/casper_xps/gpio.sci');
exec('scilab_library/scilab_blocks/casper_xps/swreg.sci');
// create the blocks
rfsoc4x2_inst = rfsoc4x2("define");
gpio_inst = gpio("define");
swreg_out_inst = swreg("define");
// add the blocks to the palette
cur_dir = pwd();
xps_fig_dir = cur_dir + '/scilab_library/scilab_blocks/casper_xps/figures/';
pal = xcosPal("CASPER XPS");
pal = xcosPalAddBlock(pal, rfsoc4x2_inst, xps_fig_dir + 'rfsoc4x2.png', xps_fig_dir + 'rfsoc4x2.png');
pal = xcosPalAddBlock(pal, gpio_inst, xps_fig_dir + 'gpio.png', xps_fig_dir + 'gpio.png');
pal = xcosPalAddBlock(pal, swreg_out_inst, xps_fig_dir + 'swreg.png',xps_fig_dir + 'swreg.png');
//pal = xcosPalAddBlock(pal, swreg_out_inst);
xcosPalAdd(pal);
disp('------ CASPER XPS loaded --------');

// add casper dsp blocks
disp('------Loading CASPER DSP...------');
// load the xps blocks
exec('scilab_library/scilab_blocks/casper_dsp/adder.sci');
// create the blocks
adder_inst = adder("define");
cur_dir = pwd();
dsp_fig_dir = cur_dir + '/scilab_library/scilab_blocks/casper_dsp/figures/';
pal = xcosPal("CASPER DSP");
pal = xcosPalAddBlock(pal, adder_inst, dsp_fig_dir + 'adder.png', dsp_fig_dir + 'adder.png');
xcosPalAdd(pal);
disp('------ CASPER DSP loaded --------');

// add casper sim blocks
disp('------Loading CASPER SIM...------');
// load the xps blocks
exec('scilab_library/scilab_blocks/casper_sim/constant.sci');
exec('scilab_library/scilab_blocks/casper_sim/scope.sci');
// create the blocks
constant_inst = constant("define");
scope_inst = scope("define");
cur_dir = pwd();
sim_fig_dir = cur_dir + '/scilab_library/scilab_blocks/casper_sim/figures/';
pal = xcosPal("CASPER SIM");
pal = xcosPalAddBlock(pal, constant_inst, sim_fig_dir + 'constant.png', sim_fig_dir + 'constant.png');
pal = xcosPalAddBlock(pal, scope_inst, sim_fig_dir + 'scope.png', sim_fig_dir + 'scope.png');
xcosPalAdd(pal);
disp('------ CASPER SIM loaded --------');