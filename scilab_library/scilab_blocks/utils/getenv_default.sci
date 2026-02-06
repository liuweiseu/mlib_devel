function [envvar] = getenv_default(env, default)
    try
        envvar = getenv(env);
    catch
        envvar = default;
    end
endfunction