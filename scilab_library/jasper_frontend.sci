function [build_cmd] = jasper_frontend(fn)
    // create a dir for the project
    [path, name, ext] = fileparts(fn);
    // chdir(path);
    mkdir(path+name);
    // chdir(name);
    // disp some info
    disp('Starting jasper for model: '+ name);

    // generate a fake modelpath for exec_flow.py
    modelpath = fn;

    // load the diagram file
    scs_m = xcosDiagramToScilab(fn);
    // get the number of objs
    n_objs = length(scs_m.objs);
    // go through all of the link objs, 
    // and generate the port names for each blk_obj based on the link objs.
    // the port info is stored in a struct.
    port_info = list();
    // create a struct for each blk_obj
    // some of the blk_objs are link objs, we don't need to generate port names for them
    for i = 1:n_objs
        port_info(i) = struct();
        port_info(i)('in') = list();
        port_info(i)('out') = list();
    end
    link_info = list();
    ind = 1;
    // go through all of the objs
    for i = 1:n_objs
        obj = scs_m.objs(i);
        // check the obj type
        // if it's a link obj, we used generate port name based on this obj
        if typeof(obj) == 'Link' then
            [blk_port_info] = gen_port_info(name, scs_m.objs, obj);
            src_blk_id = blk_port_info('src_blk_id');
            src_port_name = blk_port_info('src_port_name');
            src_port_id = blk_port_info('src_port_id');
            if src_blk_id ~= -1 then
                    port_info(src_blk_id)('out')(src_port_id) = src_port_name;
            end
            dst_blk_id = blk_port_info('dst_blk_id');
            dst_port_name = blk_port_info('dst_port_name');
            dst_port_id = blk_port_info('dst_port_id');
            // if the dst_blk_id is -1, it means the dst_blk is a SPLIT_f block
            if dst_port_id ~= -1 then
                port_info(dst_blk_id)('in')(dst_port_id) = dst_port_name;
            end
            // if the dst_blk is not a SPLIT_f block, we will save the struct to link_info
            if dst_blk_id ~= -1 then
                link_info(ind) = blk_port_info;
                ind = ind + 1;
            end
        end
    end
    // query the block information
    st = struct();
     st('project') = struct('tag', 'proj', 'filename', fn);
     blkid = 1;
     linkid = 1;
     for i = 1:n_objs
         obj = scs_m.objs(i);
         // check the obj type
         // if it's a block, get the block info
         if typeof(obj) == 'Block' then
             // if it's a split_f block, we don't need to get the info
             if obj.gui == 'SPLIT_f' then
                 // this is a special block, we don't need to get the info
                 // st('blk.'+string(blkid))= struct('type', 'scilab-blk', 'tag', 'scilab-blk:'+obj.gui, 'blkid', i);
                 // blkid = blkid + 1;
                 continue;
             end
             // we need graphics.exprs
             val = obj.graphics.exprs;
             id = obj.model.rpar;
             type = obj.model.label;
             // then we need to create a struct for the info
             st('blk.'+string(blkid))= struct('type', type, 'tag', obj.gui, 'blkid', i, 'id', id, 'val', val);
             blkid = blkid + 1;
         end
         // if it's a link obj, get the link info
         if typeof(obj) == 'Link' then
             // from/to have three digits
             // here is the detailed info about these three digits:
             // https://help.scilab.org/docs/2024.1.0/en_US/scicos_link.html
             //st('link.'+string(linkid))= struct('tag', 'link', 'linkid', linkid, 'from', obj.from, 'to', obj.to);
             //linkid = linkid + 1;
             continue;
         end
     end
    st('link_info') = link_info;
    // create a big struct
    toJSON(st, 'jasper.json', 4);
    // BUG: this looks like a bug in scilab
    // not sure why we have to clear the variables
    // if we don't do it, the python script will not work...
    clear st;
    clear port_info;
    clear link_info;
    clear id;
    clear val;
    clear type;
    clear blkid;
    // execute a python script to read the json file and generate jasper.per
    disp('****************************************');
    disp('*  Frontend python script is running...*');
    scilab_library_path = getenv('MLIB_DEVEL_PATH')+'/scilab_library';
    unix_s(scilab_library_path+'/jasper_frontend.py');
    disp('*  Frontend python script complete!    *');
    disp('****************************************');
    build_cmd = struct();
    python_path = 'python';
    // create a build_cmd for the dsp project
    jasper_python = [getenv('MLIB_DEVEL_PATH')+'/scilab_library/gen_dsp_ip.py'];
    build_cmd('dsp') = python_path + ' ' + jasper_python + ' '+ '-m ' + modelpath;
    // create a build_cmd for the full project
    jasper_python = [getenv('MLIB_DEVEL_PATH')+'/jasper_library/exec_flow.py'];
    build_cmd('full') = python_path + ' ' + jasper_python + ' '+ '-m ' + modelpath + ' --middleware --backend --software --vitis';

endfunction