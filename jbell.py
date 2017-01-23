#-*- coding: utf-8 -*-
import sys, shlex
from os import fork,popen,chdir,execvp,WIFEXITED,WIFSIGNALED,waitpid
import getpass

built_in_cmds = {}

def get_pwd():
    p = popen("pwd")
    output = p.read()
    p.close()
    return output[:-1]

def get_ls():
    p = popen("ls")
    output = p.read()
    p.close()
    return output

def cd(args):
    if args:
        try :
            chdir(args[0])
        except OSError as e:
            print "No such file or directory"

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
    while status == 1:
        pwd = get_pwd()
        sys.stdout.write("user:" + getpass.getuser() +" " + pwd + ' > ')
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
    
    pid = fork()
    if pid == 0:
    # Child process
        # Replace the child shell process with the program called with exec
        try:
            execvp(cmd_tokens[0], cmd_tokens)
        except OSError as e:
            print "Error: jbell doesnt recognise given command"
        
    elif pid > 0:
    # Parent process
        while True:
            # Wait response status from its child process (identified with pid)
            wpid, status = waitpid(pid, 0)

            # Finish waiting if its child process exits normally
            # or is terminated by a signal
            if WIFEXITED(status) or WIFSIGNALED(status):
                break

    # Return status indicating to wait for next command in shell_loop
    return 1

if __name__ == "__main__":
    main()
