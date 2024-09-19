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
                st('blk.'+string(blkid))= struct('type', 'scilab-blk', 'tag', 'scilab-blk:'+obj.gui, 'blkid', i);
                blkid = blkid + 1;
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
            st('link.'+string(linkid))= struct('tag', 'link', 'linkid', linkid, 'from', obj.from, 'to', obj.to);
            linkid = linkid + 1;
        end
    end
    // create a big struct
    toJSON(st, 'jasper.json', 4)
    // execute a python script to read the json file and generate jasper.per
    disp('****************************************');
    disp('*  Frontend python script is running...*');
    scilab_library_path = getenv('MLIB_DEVEL_PATH')+'/scilab_library';
    unix_s(scilab_library_path+'/jasper_frontend.py');
    disp('*  Frontend python script complete!    *');
    disp('****************************************');
    // create a build_cmd
    jasper_python = [getenv('MLIB_DEVEL_PATH')+'/jasper_library/exec_flow.py'];
    python_path = 'python'
    build_cmd = python_path + ' ' + jasper_python + ' '+ '-m ' + modelpath + ' --middleware --backend --software --vitis';

endfunction