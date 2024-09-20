// this function generates a unique port name for a given block
function [port_info] = gen_port_info(proj_name, blk_objs, link_obj)
    // Note: Actually, the blk_objs contains all of the objs, including link objs.
    // check the dst obj first
    obj_to_id = link_obj.to(1);
    obj_to = blk_objs(obj_to_id);
    dst_blk_tag = obj_to.gui;
    dst_port_id = link_obj.to(2);
    dst_port_dir = 'in';
    if dst_blk_tag == 'SPLIT_f' then
        disp('This is a SPLIT_f block, which will be dealt with later.');
        dst_port_name = 'Null';
        dst_port_id = -1;
        dst_blk_id = -1;
        dst_blk = 'Null';
        dst_port_width = -1;
    else
        // get the blk name
        // it's always in the first exprs
        blk_name = obj_to.graphics.exprs(1);
        // get the suffix
        suffix = gen_port_suffix(dst_blk_tag, dst_port_id, dst_port_dir);
        dst_port_name = proj_name + '_' + blk_name + '_' + suffix;
        dst_port_id = link_obj.to(2);
        dst_blk_id = obj_to_id;
        dst_blk = obj_to;
        dst_port_width = get_port_width(dst_blk, dst_port_id, dst_port_dir);
    end
    // check the source obj 
    obj_from_id = link_obj.from(1);
    obj_from = blk_objs(obj_from_id);
    // the obj tag is set in the gui field.
    src_blk_tag = obj_from.gui;
    src_port_id = link_obj.from(2);
    src_port_dir = 'out';
    if src_blk_tag == 'SPLIT_f' then
        // the SPLIT_f block is a split block, which is annoying...
        // we need to check where the split block is connected from, and then do a direct connect
        [src_blk_id, src_blk, src_port_id, src_port_dir] = search_for_src_blk(blk_objs, obj_from_id);
        blk_name = src_blk.graphics.exprs(1);
        src_blk_tag = src_blk.gui;
        suffix = gen_port_suffix(src_blk_tag, src_port_id, src_port_dir);
        src_port_name = proj_name + '_' + blk_name + '_' + suffix;
        src_blk = blk_objs(src_blk_id);
        src_port_width = get_port_width(src_blk, src_port_id, src_port_dir);
    else
        // get the blk name
        // it's always in the first exprs
        blk_name = obj_from.graphics.exprs(1);
        // get the suffix
        suffix = gen_port_suffix(src_blk_tag, src_port_id, src_port_dir);
        src_port_name = proj_name + '_' + blk_name + '_' + suffix;
        src_port_id = link_obj.from(2);
        src_blk_id = obj_from_id;
        src_blk = obj_from;
        src_port_width = get_port_width(src_blk, src_port_id, src_port_dir);
    end
    port_info = struct();
    port_info('src_blk_id') = src_blk_id;
    port_info('src_port_name') = src_port_name;
    port_info('src_port_id') = src_port_id;
    port_info('src_port_width') = src_port_width;
    port_info('dst_blk_id') = dst_blk_id;
    port_info('dst_port_name') = dst_port_name;
    port_info('dst_port_id') = dst_port_id;
    port_info('dst_port_width') = dst_port_width;
    // check the link type: xps-xps, dsp-dsp, xps-dsp, dsp-xps
    if dst_blk_id ~= -1 then
        port_info('link_type') = src_blk.model.label + '-' + dst_blk.model.label;
    else
        port_info('link_type') = 'Null';
    end
endfunction