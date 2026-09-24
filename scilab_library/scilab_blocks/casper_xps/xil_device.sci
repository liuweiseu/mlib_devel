// xil_device: Xinlinx AXI4 IP-core marker block, PyQt6-mask pattern,
// hand-written (not gen_sci_block.py). Per xps_library's own description
// ("used by casper toolflow developers, not normal users") and confirmed
// by inspecting xps_library.slx's internal system XML directly: this
// SubSystem has no "Ports" property at all (unlike every other Memory-group
// block, which all show a real [in, out] Ports vector) -- i.e. it is a
// pure design-wide marker with mask parameters (BaseAddress/MemorySize/Type)
// but no signal path, the same "zero ports" shape as every Platforms-group
// block (see rfsoc4x2.sci).
function [x, y, typ] = xil_device(job, arg1, arg2)
    x=[];y=[];typ=[];
    select job
    case 'set' then
        x = arg1;
        export_exprs_to_tmpdir(x);
        bconfig = run_mask(x);
        x = update_exprs_from_tmpdir(x);
        x = xil_device_refresh(x, bconfig);
    case 'define' then
        tag = 'xil_device';
        model = scicos_model();
        model.sim = list(tag, 4);
        model.blocktype = 'c';
        model.label = tag;
        model.rpar = [];
        gr_i = [];
        exprs = [];
        x=standard_define([7.2 6],model,exprs,gr_i)
        x.graphics.style = 'shape=rectangle;fillColor=yellow';
        x = init_exprs(x);
        debug_info('xil_device block loaded...')
    end
endfunction

function [x] = xil_device_refresh(obj, bconfigfn)
    // zero-port block -- nothing to resize/rewire, just keep the fill
    // style consistent (mirrors every other casper_xps block's 'set' path).
    x = obj;
    graphics = x.graphics;
    graphics.style = 'shape=rectangle;fillColor=yellow';
    x.graphics = graphics;
endfunction
