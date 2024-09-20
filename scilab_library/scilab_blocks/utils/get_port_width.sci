// this function returns the port witdh of the block
function [port_width] = get_port_width(blk_obj, port_id, port_dir)
    // check the block type
    blk_tag = blk_obj.gui;
    if blk_tag == 'swreg' then
        // for the swreg block, the port width is the 7th exprs
        // we don't care about the port_id and port_dir for swreg
        port_width = strtod(blk_obj.graphics.exprs(7));
    elseif blk_tag == 'gpio' then
        // for the gpio block, the port width is the 6th exprs
        port_width = strtod(blk_obj.graphics.exprs(6));
    elseif blk_tag == 'adder' then
        if port_dir == 'in' then
            // for the adder block, the port width is the 1st and 2nd exprs
            port_width = strtod(blk_obj.graphics.exprs(port_id + 1));
        elseif port_dir == 'out' then
            // for the adder block, the port width is the 3rd exprs
            port_width = strtod(blk_obj.graphics.exprs(port_id + 3));
        end
    else
        // TODO: add more port width
        break;
    end
    
endfunction