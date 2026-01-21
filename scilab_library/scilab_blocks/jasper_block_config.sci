function [] = jasper_block_config(fn, blkname)
    disp('Design Name: '+ fn);
    disp('Configuring Block: '+ blkname);
    // generate block config files first
    gen_all_blocks_config(fn);
    // there is an env var set in gen_all_blocks_config,
    // we can use it directly.
    configdir = getenv('CONFIG_DIR');
    // with the configdir and the blk, we can get the blk config file
    blk_config_file = configdir + '/' + blkname + '.json';
    disp('BLK config file: ' + blk_config_file);
    // get the config
    blk_config = fromJSON(blk_config_file, "file");
    tag = blk_config('parameters')('tag');
    mtype = strsplit(tag, ':')(2);
    // create the script to call the GUI script
    python_path = 'python';
    python_script = [getenv('MLIB_DEVEL_PATH')+'/scilab_library/block_guis/' + mtype + '/mask.py'];
    python_args = '-s ' + blk_config_file + ' ' + '-d ' + blk_config_file + ' ' + '-l ' + configdir;
    cmd = python_path + ' ' + python_script + ' ' + python_args;
    debug_info('Block Config Cmd: ' + cmd);
    unix_w(cmd);
    // get the block index
    index = search_block_by_name(fn, blkname);
    
endfunction