function [] = jasper(fn)
    build_cmd = jasper_frontend(fn);
    disp('****************************************')
    disp('*  Frontend complete!                  *')
    disp('*  Running Backend generation          *')
    disp('****************************************')
    disp('****************************************')
    disp('*  Compiling the model...              *')
    disp('****************************************')
    unix_w(build_cmd);
    disp('****************************************')
    disp('*  Backend complete!                   *')
    disp('****************************************')
endfunction