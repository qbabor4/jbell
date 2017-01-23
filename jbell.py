#-*- coding: utf-8 -*-
import sys, shlex, os

built_in_cmds = {}

def get_pwd():
    p = os.popen("pwd")
    output = p.read()
    p.close()
    return output[:-1]

def cd(args):
    os.chdir(args[0])

    return 1

def exit(args):
    return 0

def init():
    register_command("cd", cd)
    register_command("exit", exit)

def register_command(name, func):
    built_in_cmds[name] = func

def shell_loop():
    # start loop
    status = 1
    pwd = get_pwd()
    while status == 1:
        sys.stdout.write(pwd + ' > ')
        sys.stdout.flush()

        cmd = sys.stdin.readline()
        cmd_tokens = tokenize(cmd)
        status = execute(cmd_tokens)
    
def main():
    init()
    shell_loop()

def tokenize(string):
    return shlex.split(string)

def execute(cmd_tokens):
    # Fork a child shell process
    # If the current process is a child process, its `pid` is set to `0`
    # else the current process is a parent process and the value of `pid`
    # is the process id of its child process.
    # Extract command name and arguments from tokens
    cmd_name = cmd_tokens[0]
    cmd_args = cmd_tokens[1:]

    # If the command is a built-in command, invoke its function with arguments
    if cmd_name in built_in_cmds:
        return built_in_cmds[cmd_name](cmd_args)
    
    pid = os.fork()
    if pid == 0:
    # Child process
        # Replace the child shell process with the program called with exec
        os.execvp(cmd_tokens[0], cmd_tokens)
    elif pid > 0:
    # Parent process
        while True:
            # Wait response status from its child process (identified with pid)
            wpid, status = os.waitpid(pid, 0)

            # Finish waiting if its child process exits normally
            # or is terminated by a signal
            if os.WIFEXITED(status) or os.WIFSIGNALED(status):
                break

    # Return status indicating to wait for next command in shell_loop
    return 1

if __name__ == "__main__":
    main()
