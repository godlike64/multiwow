import subprocess
import shlex

def get_window_ids(command, name):
    """Get Window IDs matching 'name', using 'command'.
    
    This function and get_vd_window_ids will only work normally if WoW is run 
    in virtual desktop mode. See the README for details."""
    ids_vd = get_vd_window_ids(name)
    ids = []
    for id in ids_vd:
        result = run_cmd(
            command.format(id=id),
            use_shlex=False,
            shell=True,
        )
        ids.append(int(result.stdout))
    return ids

def get_vd_window_ids(name):
    """Get virtual desktop window IDs matching 'name', using 'command'.
    
    This function and get_window_ids will only work normally if WoW is run 
    in virtual desktop mode. See the README for details."""
    result = run_cmd(f'xdotool search --name {name}')
    ids_raw = result.stdout.decode('utf-8').split('\n')
    ids_vd = [int(id) for id in filter(None, ids_raw)]
    return ids_vd

def run_cmd(command, use_shlex=True, shell=False):
    """Helper function to wrap subprocess.run invocations."""
    if use_shlex:
        command = shlex.split(command)
    result = subprocess.run(command, shell=shell, stdout=subprocess.PIPE)
    return result
    
