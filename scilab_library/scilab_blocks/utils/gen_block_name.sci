/* generate the block name automatically */
/* store the name in a json file under builddir */
function [name] = gen_block_name(builddir, obj)
    blistfn = sprintf("%s/block_list.json", builddir);
    // check if block list exists
    if isfile(blistfn) then
        blist = fromJSON(blistfn, 'file');
    else
        blist = struct();
    end
    // check if the key exists
    tag = get_block_tag(obj);
    if isfield(blist, tag) then
        nobjs = blist(tag)('nobjs');
    else
        blist(tag) = struct();
        nobjs = 0;
    end
    // let's create the block name!
    name = sprintf("%s_%d", tag, nobjs);
    nobjs = nobjs + 1;
    uid = gen_uid(obj);
    // write the info back to the blist
    blist(tag)('nobjs') = nobjs;
    blist(tag)(uid) = name;
    toJSON(blist, blistfn, 4);
    debug_info('New Block Collected: ' + name);
endfunction