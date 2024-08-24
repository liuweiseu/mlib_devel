loadXcosLibs;

disp('------Loading CASPER XPS...------');

// load the scilab functions
exec('scilab_library/jasper.sci');
exec('scilab_library/jasper_frontend.sci');

// load the xps blocks
exec('scilab_library/casper_xps/rfsoc4x2.sci');
exec('scilab_library/casper_xps/gpio.sci');
exec('scilab_library/casper_xps/swreg.sci');

// create the blocks
rfsoc4x2_inst = rfsoc4x2("define");
gpio_inst = gpio("define");
swreg_out_inst = swreg("define");

// add the blocks to the palette
cur_dir = pwd();
pal = xcosPal("CASPER XPS");
pal = xcosPalAddBlock(pal, rfsoc4x2_inst, cur_dir + '/scilab_library/casper_xps/figures/rfsoc4x2.png', cur_dir + '/scilab_library/casper_xps/figures/rfsoc4x2.png');
pal = xcosPalAddBlock(pal, gpio_inst, cur_dir + '/scilab_library/casper_xps/figures/gpio.png', cur_dir + '/scilab_library/casper_xps/figures/gpio.png');
pal = xcosPalAddBlock(pal, swreg_out_inst, cur_dir + '/scilab_library/casper_xps/figures/swreg.png',cur_dir + '/scilab_library/casper_xps/figures/swreg.png');
xcosPalAdd(pal);

disp('------CASPER XPS loaded------');
