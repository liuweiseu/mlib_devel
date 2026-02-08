/* remove the tmp dir for bconfigs */
function [status] = remove_tmpdir()
    tmpdir = getenv_default('BCONFIG_TMPDIR', '/tmp/casper_bconfigs');
    status = rmdir(tmpdir, 's');
endfunction