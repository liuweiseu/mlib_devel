#! /usr/bin/env python
import json, yaml
import os
from datetime import datetime
from utils.design_info import gen_design_info
from utils.git_info import gen_git_info
from mlib_devel.scilab_library.utils.gen_link_info import gen_link_info

# write the blkinfo to the dict
def write_blkinfo_to_dict(blk_info, blk_tmp):
    # make a copy of the dict
    template = blk_tmp.copy()
    keys = list(template.keys())
    index = blk_info['id']
    for i in range(len(index)):
        try:
            template[keys[index[i][0]]] = int(blk_info['val'][i][0])
        except:
            try:
                template[keys[index[i][0]]] = float(blk_info['val'][i][0])
            except:
                if blk_info['val'][i][0] == 'on':
                    template[keys[index[i][0]]] = True
                elif blk_info['val'][i][0] == 'off':
                    template[keys[index[i][0]]] = False
                else:
                    template[keys[index[i][0]]] = blk_info['val'][i][0]
    # go through all of the k-v pairs in the template, 
    # and modify all of the 'on' to True and 'off' to False
    for k, v in template.items():
        if v == 'on':
            template[k] = True
        elif v == 'off':
            template[k] = False
    return template

# dump the jasper_dict to jasper.per
def dump_jasper(jasper_per, fn = 'jasper.per'):
    f = open(fn, 'w+')
    yaml.dump(jasper_per, f, sort_keys=False)
    f.close()

# get the scilab path from the environment variable
scilab_library_path = os.getenv('MLIB_DEVEL_PATH')+ '/scilab_library'
# open the jasper.json file
with open('jasper.json') as f:
    blkinfo = json.load(f)
# after reading the file, remove it
# os.remove('jasper.json')
# open the block_info_template.json file
with open('%s/block_info_template.json'%(scilab_library_path)) as f:
    blkinfo_template = json.load(f)

# get the proj name
blkfn = blkinfo['project']['filename']
proj_name = blkfn.split('/')[-1].split('.')[0]
filepath = blkfn.split('.')[0]

# get the scilab blk, blk objs and link objs from the jaser.json file
scilab_blk_objs = []
blk_objs = []
link_objs = []
for k, v in blkinfo.items():
    if k.startswith('blk'):
        if v['tag'].startswith('scilab-blk'):
            scilab_blk_objs.append(v)
        else:
            blk_objs.append(v)
    if k.startswith('link'):
        link_objs.append(v)

# genenrate yellow blocks dict
yellow_blocks = {}
for blk in blk_objs:
    tag = blk['tag']
    # check if the block in the blockinfo starts with xps
    if blkinfo_template[tag]['tag'].startswith('xps'):
        # populate yellow block
        key = proj_name + '/' + blk['val'][0][0]
        yellow_blocks[key] = write_blkinfo_to_dict(blk, blkinfo_template[tag])
        yellow_blocks[key]['fullpath'] = key

# generate user_module dict
user_modules = {}
# TODO: as we are adding dsp blocks in the design, we need to re-write code for the user_module
'''
user_module_dict = gen_ip(blkinfo)
for k,v in user_module_dict.items():
    user_modules[k] = {}
    # populate clock
    user_modules[k]['clock'] = 'clk'
    # populate ports
    user_modules[k]['ports'] = []
    for port in v['in']:
        user_modules[k]['ports'].append(port)
    for port in v['out']:
        user_modules[k]['ports'].append(port)
    # populate sources
    user_modules[k]['sources'] = []
    user_modules[k]['sources'].append('%s/%s.v'%(filepath, k))
'''
# generate jasper.per
jasper_per = {}
jasper_per['yellow_blocks'] = yellow_blocks
jasper_per['user_modules'] = user_modules
#jasper_per_str = json.dumps(jasper_per, indent=2)
#print(jasper_per_str)
dump_jasper(jasper_per, fn='%s/jasper.per'%(filepath)) 

# now, we need to generate jasper.dsp, which contains the dsp block info
dsp_blocks = {}
for blk in blk_objs:
    tag = blk['tag']
    # check if the block in the blockinfo starts with dsp or xps:xsg
    # we need xps:xsg as it contains the platform info
    if blkinfo_template[tag]['tag'].startswith('dsp') or blkinfo_template[tag]['tag'] == 'xps:xsg':
        # populate dsp block
        key = proj_name + '/' + blk['val'][0][0]
        dsp_blocks[key] = write_blkinfo_to_dict(blk, blkinfo_template[tag])
        dsp_blocks[key]['fullpath'] = key
# generate jasper.dsp
jasper_dsp = {}
jasper_dsp['dsp_blocks'] = dsp_blocks
#jasper_dsp_str = json.dumps(jasper_dsp, indent=2)
#print(jasper_dsp_str)
dump_jasper(jasper_dsp, fn='%s/jasper.dsp'%(filepath))

# generate design_info.tab
gen_design_info(yellow_blocks, proj_name, fn='%s/design_info.tab'%(filepath))
# generate git_info.tab
gen_git_info(proj_name, fn='%s/git_info.tab'%(filepath))

