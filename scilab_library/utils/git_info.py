import os
import subprocess

def gen_git_info(blk, fn='git_info.tab'):
    r = []
    # TODO: we need to do a lot of checks first
    mlib_devel_path = os.getenv('MLIB_DEVEL_PATH')
    # get blk version
    script_path = '%s/xps_library/get_git_info.py'%(mlib_devel_path)
    cmd = ['python', script_path, '--fpgstring', blk]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    [out, err] = p.communicate()
    # TODO: check the err
    r.append(out.decode('utf-8'))
    # get mlib_devel version
    cmd = ['python', script_path, '--fpgstring', mlib_devel_path]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    [out, err] = p.communicate()
    # TODO: check the err
    r.append(out.decode('utf-8'))
    # write to file
    with open(fn, 'w') as f:
        f.writelines(r)
    