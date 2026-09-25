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
    /* check if any two blocks in the design share the same name. */
    dup_msg = check_duplicate_names(fn);

    if nxsg == 1 & dup_msg == '' then
        validation = 'ok';
    else
        validation = ascii(10) + '**************Validation Failed**************';
        if nxsg <> 1 then
            validation = validation + ascii(10) + 'Please use a platform block in the design.';
            validation = validation + ascii(10) + '*********************************************';
        end
        if dup_msg <> '' then
            validation = validation + ascii(10) + dup_msg;
            validation = validation + ascii(10) + '*********************************************';
        end
        validation = validation + ascii(10);
    end
endfunction