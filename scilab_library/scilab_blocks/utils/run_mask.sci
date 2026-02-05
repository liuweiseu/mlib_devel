function [cmd] = run_mask(obj)
    mlib_devel_path = getenv('MLIB_DEVEL_PATH');
    uid = gen_uid(obj);
    mask = sprintf("%s/scilab_library/block_guis/%s/mask.py", mlib_devel_path, obj.gui); 
    debug_info('mask: ' + mask);
    template = sprintf("%s/scilab_library/scilab_blocks/casper_%s/%s.json", mlib_devel_path, obj.model.label, obj.gui);
    debug_info('template: ' + template);
    target = sprintf("/tmp/casper_bconfigs/%s.json", uid);
    cmd = sprintf("python %s --template %s --target %s", mask, template, target);
    debug_info('cmd: ' + cmd);
    unix_w(cmd);
endfunction