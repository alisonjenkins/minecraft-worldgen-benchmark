#!/usr/bin/env python2
import os
import sys
import os.path
import ConfigParser
import subprocess
import shlex
import time
import re
import datetime

def load_bench_config(config_path):
    if not os.path.exists(config_path):
        print("Config file %s is missing, aborting." % config_path)
        sys.exit(1)
    else:
        config = ConfigParser.ConfigParser()
        config.read(config_path)
        return config

# move mods to test to mods dir
def move_test_mods_to_server_mods(mods):
    for mod in mods:
        dest_dirpath = os.path.split(mod.dest_path)[0]
        if not os.path.exists(dest_dirpath):
            os.makedirs(dest_dirpath)
        shutil.copyfile(mod.source_path, mod.dest_path)


def clear_mods_dir(path):
    for dirpath, dirnames, filenames in os.walk(path, topdown=False):
        for filename in filenames:
            remove_name = os.path.join(dirpath, filename)
            os.remove(remove_name)
        os.rmdir(dirpath)
    os.mkdir(path)

def delete_old_logs(server_dir):
    log_files = ['ForgeModLoader-server-0.log', 'ForgeModLoader-server-0.log.lck', 'ForgeModLoader-server-1.log', 'ForgeModLoader-server-2.log', 'server.log']

    for log_file in log_files:
        log_path = os.path.join(server_dir, log_file)
        if os.path.exists(log_path):
            os.remove(log_path)

def delete_old_world(server_dir):
    world_path = os.path.join(server_dir, 'world')
    if os.path.exists(world_path):
        print("Deleting old world")

        for dirpath, dirs, files in os.walk(world_path, topdown=False):
            for filename in files:
                filepath = os.path.join(dirpath,filename)
                os.remove(filepath)

            for directory in dirs:
                rmdirpath = os.path.join(dirpath, directory)
                os.rmdir(rmdirpath)
        os.rmdir(world_path)

def delete_worldborder_config(server_dir):
    config_path = os.path.join(server_dir, 'plugins/WorldBorder/config.yml')
    if os.path.exists(config_path):
        print("Deleting WorldBorder config.")
        os.remove(config_path)

def start_server(path, mcpc_jar_name):
    commands = [
            'tmux new-session -d -n worldgenbench:0 -s worldgenbench',
            'tmux -q send -t worldgenbench:worldgenbench \"java -Xmn512M -Xms14096M -Xmx14096M -XX:MaxPermSize=1024M -jar %s\" C-m' % mcpc_jar_name
            ]
    for command in commands:
        subprocess.Popen(shlex.split(command), cwd='server')

def wait_for_server_start(path):
    time.sleep(5)
    server_logfile_path = os.path.join(path, 'server.log')
    if not os.path.exists(os.path.abspath(server_logfile_path)):
        print("%s does not exist." % os.path.abspath(server_logfile_path))
    server_logfile = open(server_logfile_path)
    loglines = follow(server_logfile)

    re_server_spawn = re.compile('For reference, the main world\'s spawn location is at X: (?P<X>[\-0-9.]+) Y: (?P<Y>[\-0-9.]+) Z: (?P<Z>[\-0-9.]+)')
    re_server_started = re.compile('Done \((?P<starttime>.*?)s\)! For help, type \"help\" or \"?\"')
    server_spawn = False
    start_time = False

    for line in loglines:
        print(line),
        if server_spawn == False:
            match = re_server_spawn.search(line)
            if match:
                server_spawn = {}
                server_spawn['X'] = match.group('X')
                server_spawn['Y'] = match.group('Y')
                server_spawn['Z'] = match.group('Z')
                print("Found server spawn at %s, %s, %s" % (server_spawn['X'], server_spawn['Y'], server_spawn['Z']))
            # else:
            #     print("%s did not match spawn re." % line)
        if start_time == False:
            match = re_server_started.search(line)
            if match:
                start_time = match.group('starttime')
                print('Server started. Took %s' % start_time)
            # else:
            #     print("%s did not match server started re" % line)
        if start_time and server_spawn:
            break

    return [server_spawn, start_time]

def start_generation(radius, spawnx, spawnz):
    time.sleep(1)
    commands = [
            'tmux -q send -t worldgenbench:worldgenbench \"wb world set %i %s %s\" C-m' % (radius, spawnx, spawnz),
            'tmux -q send -t worldgenbench:worldgenbench \"wb shape square\" C-m',
            'tmux -q send -t worldgenbench:worldgenbench \"wb world fill 1000 208 true\" C-m',
            'tmux -q send -t worldgenbench:worldgenbench \"wb fill confirm\" C-m'
            ]
    for command in commands:
        subprocess.Popen(shlex.split(command), cwd='server')
        time.sleep(0.2)
    return datetime.datetime.now()

def await_completion(path):
    server_logfile_path = os.path.join(path, 'server.log')
    if not os.path.exists(os.path.abspath(server_logfile_path)):
        print("%s does not exist." % os.path.abspath(server_logfile_path))
    server_logfile = open(server_logfile_path)
    loglines = follow(server_logfile)

    re_complete = re.compile('For reference, the main world\'s spawn location is at X: (?P<X>[\-0-9.]+) Y: (?P<Y>[\-0-9.]+) Z: (?P<Z>[\-0-9.]+)')
#     re_server_started = re.compile('Done \((?P<starttime>.*?)s\)! For help, type \"help\" or \"?\"')
#     server_spawn = False
#     start_time = False
# 
#     for line in loglines:
#         print(line),
#         if server_spawn == False:
#             match = re_server_spawn.search(line)
#             if match:
#                 server_spawn = {}
#                 server_spawn['X'] = match.group('X')
#                 server_spawn['Y'] = match.group('Y')
#                 server_spawn['Z'] = match.group('Z')
#                 print("Found server spawn at %s, %s, %s" % (server_spawn['X'], server_spawn['Y'], server_spawn['Z']))
#             # else:
#             #     print("%s did not match spawn re." % line)
#         if start_time == False:
#             match = re_server_started.search(line)
#             if match:
#                 start_time = match.group('starttime')
#                 print('Server started. Took %s' % start_time)
#             # else:
#             #     print("%s did not match server started re" % line)
#         if start_time and server_spawn:
#             break
# 
#     return [server_spawn, start_time]
# 
# 
def follow(thefile):
    thefile.seek(0,2)      # Go to the end of the file
    while True:
         line = thefile.readline()
         if not line:
             time.sleep(0.1)    # Sleep briefly
             continue
         yield line

