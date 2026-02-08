/* 
check if the design meets the basic requirements:
1. the design has to contain a platform block.
*/
function [validation] = validate_design(fn)
    /* load the diagram file */
    scs_m = xcosDiagramToScilab(fn);
    /* get the number of objs */
    n_objs = length(scs_m.objs);
    /* check if one platform block is in the design. */
    nxsg = 0;
    for i = 1:n_objs
        obj = scs_m.objs(i);
        /* if it's a block, get the block info */
        if typeof(obj) == 'Block' then
            tag = get_block_tag(obj);
            btype = get_block_type(obj);
            /* if it's a split_f block, we don't need to get the info */
            if tag == 'SPLIT_f' then
                continue;
            end
            tmp = obj.graphics.exprs(3);
            xsg = strsplit(tmp, ':')($);
            if xsg == 'xsg' then
                nxsg = nxsg + 1;
            end
        end
    end
    if nxsg == 1 then
        validation = 'ok';
    else
        validation = 'Please use a platform block in the design.'
    end
endfunction