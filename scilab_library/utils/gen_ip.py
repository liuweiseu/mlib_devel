import os
# TODO: improve - we should improve the code in this file!!
# define the blk port suffix here
blk_port_suffix = {
    'swreg':{
        'in' : '_user_data_in',
        'out': '_user_data_out'
    },
    'gpio':{
        'in' : '_gateway',
        'out': '_gateway'
    }
}
# define the blk port width here
# This is the id in blk['val']
blk_port_width = {
    'swreg': 6, 
    'gpio': 5
}

# create port name for different types of blocks
# TODO: improve - this is not good, we should improve this
def create_port_name(blk, proj_name, io_dir = 'in'):
    blkname = blk['val'][0][0]
    tag = blk['tag']
    if tag == 'swreg':
        if blk['val'][1][0] == 'From Processor':
            dir = 'out'
        elif blk['val'][1][0] == 'To Processor':
            dir = 'in'
    elif tag == 'gpio':
        dir = blk['val'][3][0]
    else:
        pass
    return proj_name + '_' + blkname + blk_port_suffix[tag][dir]

# get bit width of the blk, which should be based on the blk tag
# TODO: improve - this is not good, we should improve this
def get_port_width(blk):
    id = blk_port_width[blk['tag']]
    return int(blk['val'][id][0])

# find the blk with the blkid
def find_blk(blks, blkid):
    for blk in blks:
        # the blkid is the same as the input blkid
        if blk['blkid'] == blkid:
            return blk
    return None

# check the clk type
# we will know if it's a xps block or a dsp block
def check_blk_type(blk):
    return blk['type']

def gen_user_module(module_name, in_ports, out_ports, bitwidth = 1, path = './'):
    '''
    Description: 
        Generate user module for jasper.
        The module only has one in_port, but it may have multiple out_ports.
        The only one in_port drives all of the out_ports.
    Inputs:
        - module_name(str): the name of the user module
        - in_ports(list): the names of the in_ports
        - out_ports(list): the names of the out_ports
        - bitwidth(int): the bitwidth of the in_port
        - path(str): the path to save the user module
    '''
    src_str = []
    # add module name
    src_str.append('module %s('%module_name)
    # add clock port
    src_str.append('input clk,')
    # add in_ports
    src_str.append('input [%d:0] %s,'%(bitwidth-1, in_ports[0]))
    # add out_ports
    for i in range(len(out_ports)):
        src_str.append('output [%d:0] %s,'%(bitwidth-1, out_ports[i]))
    # remove the last comma
    src_str[-1] = src_str[-1][:-1]
    # add endmodule
    src_str.append(');\n')
    # add logic
    for i in range(len(out_ports)):
        src_str.append('assign %s = %s;'%(out_ports[i], in_ports[0]))
    # add endmodule
    src_str.append('')
    src_str.append('endmodule')
    # write to file
    with open('%s/%s.v'%(path, module_name), 'w') as f:
        f.write('\n'.join(src_str))

# generate the xps and dsp link info dict
def gen_link_info(proj_name, blk_objs, link_objs, link_type = 'xps'):
    # let's go through all of the link objs, 
    # and create the user module based on the link objs.
    # We will create a user module for a link obj.
    link_info = {}
    if link_type == 'xps' or link_type == 'dsp':
        # if the link type is xps or dsp,
        # we use this branch of code to generate the link info.
        for link in link_objs:
            # TODO: check the port number, and check if it's an in or out port??
            blkid_from = link['from'][0]
            blkid_to = link['to'][0]
            # get the blk with blkid_from
            blk_from = find_blk(blk_objs, blkid_from)
            # get the blk with blkid_to
            blk_to = find_blk(blk_objs, blkid_to)
            # if blk_from or blk_to is SPLIT_f blk, 
            # we need to collect the info for split module genenration
            print(blk_from['tag'], blk_to['tag'])
            if blk_from['tag'] != 'scilab-blk:SPLIT_f' and blk_to['tag'] != 'scilab-blk:SPLIT_f':
                # this is great! easy to generate the user module
                module_name = '%s_direct_link%d'%(link_type, link['linkid'])
                if module_name not in link_info:
                    link_info[module_name] = {}
                    link_info[module_name]['in'] = []
                    link_info[module_name]['out'] = []
                    link_info[module_name]['ibits'] = []
                    link_info[module_name]['obits'] = []
                link_info[module_name]['in'].append(create_port_name(blk_from, proj_name))
                link_info[module_name]['ibits'].append(get_port_width(blk_from))
                link_info[module_name]['out'].append(create_port_name(blk_to, proj_name))
                link_info[module_name]['obits'].append(get_port_width(blk_to))
            elif blk_from['tag'] == 'scilab-blk:SPLIT_f' and blk_to['tag'] != 'scilab-blk:SPLIT_f':
                module_name = '%s_split_link%d'%(link_type, blkid_from)
                if module_name not in link_info:
                    link_info[module_name] = {}
                    link_info[module_name]['in'] = []
                    link_info[module_name]['out'] = []
                    link_info[module_name]['ibits'] = []
                    link_info[module_name]['obits'] = []
                link_info[module_name]['out'].append(create_port_name(blk_to, proj_name))
                link_info[module_name]['obits'].append(get_port_width(blk_to))
            elif blk_from['tag'] != 'scilab-blk:SPLIT_f' and blk_to['tag'] == 'scilab-blk:SPLIT_f':
                module_name = '%s_split_link%d'%(link_type, blkid_to)
                if module_name not in link_info:
                    link_info[module_name] = {}
                    link_info[module_name]['in'] = []
                    link_info[module_name]['out'] = []
                    link_info[module_name]['ibits'] = []
                    link_info[module_name]['obits'] = []
                link_info[module_name]['in'].append(create_port_name(blk_from, proj_name))
                link_info[module_name]['ibits'].append(get_port_width(blk_from))
            else:
                # it should be impossible to have both blk_from and blk_to as SPLIT_f blk
                raise ValueError('Both blk_from and blk_to are SPLIT_f blk')
    elif link_type == 'xps_dsp':
        # if the link type is xps_dsp, the ports are io ports.
        # So we just need to throw these blocks out, and label them as in blocks or out blocks.
        for link in link_objs:
            blkid_from = link['from'][0]
            blkid_to = link['to'][0]
            # get the blk with blkid_from
            blk_from = find_blk(blk_objs, blkid_from)
            # get the blk with blkid_to
            blk_to = find_blk(blk_objs, blkid_to)
            
    return link_info

# generate the port info dict
# this func will generate port info for the dsp proj and the full proj
def gen_port_info(blkinfo):
    casper_scilab_path = os.getenv('CASPER_SCILAB_PATH')
    # get the proj name and filepath from blkinfo
    blkfn = blkinfo['project']['filename']
    proj_name = blkfn.split('/')[-1].split('.')[0]
    filepath = blkfn.split('.')[0]
    # get blk objs and link objs from blkinfo
    # we will have two types of blk/link objs: dsp and xps
    # if the link is between a dsp and a xps blk, this should be a xps_dsp_link
    # Let's first get all of the blk and link objs
    blk_objs = []
    link_objs = []
    for k, v in blkinfo.items():
        if k.startswith('blk'):
            blk_objs.append(v)
        if k.startswith('link'):
            link_objs.append(v)
    """
    It looks like we don't need to separate the blk_objs into xps and dsp blks.
    We can handle this by checking the link objs.

    # now, let's see what kind of blks we have
    xps_blk_objs = []
    dsp_blk_objs = []
    for blk in blk_objs:
        if blk['type'] == 'xps':
            xps_blk_objs.append(blk)
        elif blk['type'] == 'dsp':
            dsp_blk_objs.append(blk)
        elif blk['type'] == 'scilab-blk':
            pass
        else:
            raise ValueError('The blk type is not xps or dsp')
    """
    # next, let's see what kind of links we have
    xps_link_objs = []
    dsp_link_objs = []
    xps_dsp_link_objs = []
    for link in link_objs:
        blkid_from = link['from'][0]
        blkid_to = link['to'][0]
        blk_from = find_blk(blk_objs, blkid_from)
        blk_to = find_blk(blk_objs, blkid_to)
        if check_blk_type(blk_from) == 'xps' and check_blk_type(blk_to) == 'xps':
            xps_link_objs.append(link)
        elif check_blk_type(blk_from) == 'dsp' and check_blk_type(blk_to) == 'dsp':
            dsp_link_objs.append(link)
        elif check_blk_type(blk_from) == 'xps' and check_blk_type(blk_to) == 'dsp':
            xps_dsp_link_objs.append(link)
        elif check_blk_type(blk_from) == 'dsp' and check_blk_type(blk_to) == 'xps':
            xps_dsp_link_objs.append(link)
        else:
            # TODO: this could happen, as we may have scilab-blk: SPLIT_f in the design.
            # We need to handle this case.
            raise ValueError('The link type is not xps or dsp')
        
    
    #print(module_info)
    # generate the user module based on the module_info
    for k, v in module_info.items():
        gen_user_module(k, v['in'], v['out'], v['ibits'][0], filepath)
    # return the module_info for generating jasper.per
    return module_info