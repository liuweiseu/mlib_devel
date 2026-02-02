// this function updates the scilab block.
function [] = update_scilab_block(obj, index, val)
    obj.graphics.exprs(index) = val;
endfunction