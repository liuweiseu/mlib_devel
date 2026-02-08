/* 
The block parameters are recoreded in obj.graphics.exprs.
*/
function [config] = gen_block_config(builddir, obj)
    bconfigdir = sprintf("%s/bconfigs", builddir);
    name = gen_block_name(bconfigdir, obj);
    bconfigfn = sprintf("%s/%s.json", bconfigdir, name);
    export_exprs(obj, bconfigfn);
    bconfig = fromJSON(bconfigfn, 'file');
    bconfig('parameters')('name') = name;
    projname = strsplit(builddir, '/')($);
    bconfig('parameters')('fullpath') = sprintf("%s/%s", projname, name);
    toJSON(bconfig, bconfigfn, 4);
    config = bconfig('parameters');
endfunction