function [] = jasper_block_config(fn, blkname)
    disp('Design Name: '+ fn);
    disp('Configuring Block: '+ blkname);
    // generate block config files first
    gen_all_blocks_config(fn);
    // get the block index
    index = search_block_by_name(fn, blkname);
    // open the xcos file
    scs_m = xcosDiagramToScilab(fn);
    // get the obj
    obj = scs_m.objs(index);
    // collect the specific block info
    // this will update the bconfig file
    [path, projname, ext] = fileparts(fn);
    collect_one_block_info(projname, obj);
    configdir = getenv('CONFIG_DIR');
    // with the configdir and the blk, we can get the blk config file
    blk_config_file = configdir + '/' + blkname + '.json';
    disp('BLK config file: ' + blk_config_file);
    // get the config
    blk_config = fromJSON(blk_config_file, "file");
    taginfo = blk_config('parameters')('tag');
    btype = strsplit(taginfo, ':')(1);
    tag = strsplit(taginfo, ':')(2);
    // create the script to call the GUI script
    python_path = 'python';
    python_script = [getenv('MLIB_DEVEL_PATH')+'/scilab_library/block_guis/' + tag + '/mask.py'];
    python_args = '-s ' + blk_config_file + ' ' + '-d ' + blk_config_file + ' ' + '-l ' + configdir;
    cmd = python_path + ' ' + python_script + ' ' + python_args;
    debug_info('Block Config Cmd: ' + cmd);
    unix_w(cmd);
    /****** Next, we need to update the xcos block. ******/
    // get val index
    vindex = get_block_vindex(scs_m.objs(index));
    // open bconfig.json, which was updated before
    bconfig = fromJSON(blk_config_file, "file");
    // we need the keys info from the template file
    scilab_block_path = getenv('MLIB_DEVEL_PATH')+'/scilab_library/scilab_blocks/';
    config_path = scilab_block_path + 'casper_' + btype + '/' + tag + '.json';
    bconfig_template = fromJSON(config_path, "file");
    for i = 1:length(vindex)
        // vindex starts from 0
        id = vindex(i) + 1;
        key = bconfig_template('parameters')('keys')(id)
        val = bconfig('parameters')(key)
        scs_m.objs(index).graphics.exprs(i) = val;
    end
    // xcosUpdateBlock doesn't work.
    // So we have to close the xcos file to update the block. Weird...
    // TODO: This might need to be update.
    obj = scs_m.objs(index);
    // execstr('[obj, x, y] = ' + obj.gui + '(''set'', obj)');
    port_update_func = obj.gui + '_update_ports';
    if(exists(port_update_func))
        exe = sprintf("[obj] = %s(obj, ''%s'')", port_update_func, blk_config_file);
        disp(exe);
        execstr(exe);
    end
    close xcos!;
    scs_m.objs(index) = obj;
    xcosDiagramToScilab(fn, scs_m);
    // ok, re-open the file.
    xcos(fn);
endfunction