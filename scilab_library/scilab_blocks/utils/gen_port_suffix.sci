// this function provides the suffix of the port name
// different blocks have different suffixes
// the suffix should match the port name defined in the related HDL block.
function [suffix] = gen_port_suffix(blk_tag, port_num, port_dir)
    // swreg suffix is _user_data_in or _user_data_out
    // we don't care about the port_num for swreg
    if blk_tag == 'swreg' then
        if port_dir == 'in' then
            suffix = 'user_data_in';
        else
            suffix = 'user_data_out';
        end
    // gpio suffix is gateway
    // we don't care about the port_dir and port_num for gpio
    elseif blk_tag == 'gpio' then
        suffix = 'gateway';
    // 
    elseif blk_tag == 'adder' then
        if port_dir == 'in' then
            suffix = 'in' + string(port_num-1);
        else
            suffix = 'out' + string(port_num-1);
        end
    else
        // TODO: add more suffixes
        suffix = 'i_dont_know';
    end
endfunction