// This function search for where the split block is connected from
function [src_blk_id, src_blk, port_num, port_dir] = search_for_src_blk(blk_objs, split_blk_id)
    // Note: the blk_objs contains all of the objs, including link objs.
    n_objs = length(scs_m.objs);
    for i = 1:n_objs
        obj = blk_objs(i);
        // check the obj type
        // we only need to take a look at the link objs
        if typeof(obj) == 'Link'
            // check the to field
            if obj.to(1) == split_blk_id then
                // get the src blk
                src_blk_id = obj.from(1);
                src_blk = blk_objs(src_blk_id);
                port_num = obj.from(2);
                port_dir = 'out';
                // TODO: use a struct to return the info
                return;
            end
        end
    end
endfunction