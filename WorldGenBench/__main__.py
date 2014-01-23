#!/usr/bin/env python
import os
from WorldGenMod import WorldGenMod
from funcs import clear_mods_dir, load_bench_config, delete_old_logs, delete_old_world, start_server, wait_for_server_start, start_generation, delete_worldborder_config

if __name__ == '__main__':
    # clear mods dir
    clear_mods_dir('server/mods')

    # load benchmark config.
    config = load_bench_config('bench_config.ini')

    # move mods to test to mods dir
    # move_test_mods_to_server_mods(mods)

    # delete old logs
    delete_old_logs('server')

    # delete old world
    delete_old_world('server')

    # delete WorldBorder config
    delete_worldborder_config('server')

    # start server
    start_server('server', 'mcpc-plus-1.6.4-R2.1-forge965-B223.jar')

    # wait till server started
    spawn_coords, start_time = wait_for_server_start('server')

    # record time and start world gen
    start_time = start_generation(1500, spawn_coords['X'], spawn_coords['Z'])

    # watch log for complete message
    # end_time = await_completion('server')

    # bench_time = benchmark_result(start_time, end_time)
