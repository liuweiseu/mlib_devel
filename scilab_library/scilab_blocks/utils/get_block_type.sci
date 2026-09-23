// get the block type (category).
// we have three types of blocks: xps, dsp, sim
//
// This is derived by probing for which casper_<category>/<tag>.json
// parameter template exists on disk, NOT from obj.model.label: Scicos
// aliases graphics.id (the text drawn on the block) with model.label, so
// model.label must stay free to hold the block's own display name instead
// of the category marker it used to hold.
function [type] = get_block_type(obj)
    mlib_devel_path = getenv("MLIB_DEVEL_PATH");
    tag = get_block_tag(obj);
    categories = ['dsp', 'xps', 'sim'];
    for i = 1:size(categories, '*')
        candidate = categories(i);
        fn = sprintf("%s/scilab_library/scilab_blocks/casper_%s/%s.json", mlib_devel_path, candidate, tag);
        if isfile(fn) then
            type = candidate;
            return;
        end
    end
    error(sprintf("get_block_type: no casper_<dsp|xps|sim>/%s.json found for block ""%s"".", tag, tag));
endfunction
