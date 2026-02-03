// only collect the specified one block info
function [] = collect_one_block_info(projname, obj)
    tag = get_block_tag(obj);
    btype = get_block_type(obj);
    name = get_block_name(obj);
    block_config = get_block_config(name, btype, tag);
    // create a new struct for the block info
    keys = block_config('parameters')('keys');
    vals = block_config('parameters')('values');
    block_info = struct();
    // set the default value from the block_config
    debug_info('block_config: ' + tag);
    for j = 1:size(keys)(2)
        block_info(keys(j)) = vals(j);
        debug_info('    key: ' + string(keys(j)) + ' val: ' + string(vals(j)));
    end
    blk_val = get_block_vals(obj);
    blk_vindex = get_block_vindex(obj);
    debug_info('blk_name: ' + blk_val(1))
    for j = 1:length(blk_vindex)
        id = blk_vindex(j) + 1;
        debug_info('    id: ' + string(id) + ' val: ' + string(blk_val(j)));
        block_info(keys(id)) = blk_val(j);
    end
    // set "fullpath", which should be the project name + block name
    block_info('fullpath') = projname + '/' + block_info('name');
    // update the block config in the user defined config file
    update_block_config(block_info, block_info('name'));

endfunction