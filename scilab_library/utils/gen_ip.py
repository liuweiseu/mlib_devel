import os

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
def create_port_name(blk, proj_name):
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
def get_blk_width(blk):
    id = blk_port_width[blk['tag']]
    return int(blk['val'][id][0])

# find the blk with the blkid
def find_blk(blks, blkid):
    for blk in blks:
        # the blkid is the same as the input blkid
        if blk['blkid'] == blkid:
            return blk
    return None

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

# generate the user ip
def gen_ip(blkinfo):
    casper_scilab_path = os.getenv('CASPER_SCILAB_PATH')
    # get the proj name and filepath from blkinfo
    blkfn = blkinfo['project']['filename']
    proj_name = blkfn.split('/')[-1].split('.')[0]
    filepath = blkfn.split('.')[0]
    # get blk objs and link objs from blkinfo
    blk_objs = []
    link_objs = []
    for k, v in blkinfo.items():
        if k.startswith('blk'):
            blk_objs.append(v)
        if k.startswith('link'):
            link_objs.append(v)
    # let's go through all of the link objs, 
    # and create the user module based on the link objs.
    # We will create a user module for a link obj.
    module_info = {}
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
            module_name = 'direct_link%d'%link['linkid']
            if module_name not in module_info:
                module_info[module_name] = {}
                module_info[module_name]['in'] = []
                module_info[module_name]['out'] = []
                module_info[module_name]['ibits'] = []
                module_info[module_name]['obits'] = []
            module_info[module_name]['in'].append(create_port_name(blk_from, proj_name))
            module_info[module_name]['ibits'].append(get_blk_width(blk_from))
            module_info[module_name]['out'].append(create_port_name(blk_to, proj_name))
            module_info[module_name]['obits'].append(get_blk_width(blk_to))
        elif blk_from['tag'] == 'scilab-blk:SPLIT_f' and blk_to['tag'] != 'scilab-blk:SPLIT_f':
            module_name = 'split_link%d'%blkid_from
            if module_name not in module_info:
                module_info[module_name] = {}
                module_info[module_name]['in'] = []
                module_info[module_name]['out'] = []
                module_info[module_name]['ibits'] = []
                module_info[module_name]['obits'] = []
            module_info[module_name]['out'].append(create_port_name(blk_to, proj_name))
            module_info[module_name]['obits'].append(get_blk_width(blk_to))
        elif blk_from['tag'] != 'scilab-blk:SPLIT_f' and blk_to['tag'] == 'scilab-blk:SPLIT_f':
            module_name = 'split_link%d'%blkid_to
            if module_name not in module_info:
                module_info[module_name] = {}
                module_info[module_name]['in'] = []
                module_info[module_name]['out'] = []
                module_info[module_name]['ibits'] = []
                module_info[module_name]['obits'] = []
            module_info[module_name]['in'].append(create_port_name(blk_from, proj_name))
            module_info[module_name]['ibits'].append(get_blk_width(blk_from))
        else:
            # it should be impossible to have both blk_from and blk_to as SPLIT_f blk
            pass
    #print(module_info)
    # generate the user module based on the module_info
    for k, v in module_info.items():
        gen_user_module(k, v['in'], v['out'], v['ibits'][0], filepath)
    # return the module_info for generating jasper.per
    return module_info