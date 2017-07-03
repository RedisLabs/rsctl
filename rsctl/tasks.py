import os
import itertools
from fabric.api import *
from fabric.api import run as _run
from fabric.contrib import files
from fabric.colors import yellow, red, green

import json
from rsctl import config

git_root = "git@github.com"
module_file = 'rscoordinator.zip'

apt_gets = ["git-core", "ruby", "build-essential", "gdb", 'htop', 'libuv-dev', 'python-dev', 'python-setuptools', 'python-pip', 'unzip']
pips = ['ramp-packer']

env.roledefs = {
    'rlec': [],
    'rlec_master': [],
}

@task
@parallel
@roles("rlec", "rlec_master")
def install_essentials():
    """
    Install essential build requirements for all our projects
    """
    
    # Install apt-get deps
    sudo("apt-get update && apt-get -y install {}".format(" ".join(apt_gets)))

    # Install global pip deps
    sudo('pip install {}'.format(' '.join(pips)))
    
def fetch_git_repo(namespace, name, keyFile = None):
    """
    Fetch sources from a git repo by cloning or pulling
    """

    puts(green("Cloning {} from git...".format(git_url(namespace, name))))

    with settings(warn_only=True):
        
        if files.exists(name):
            with cd(name):
                run("git pull -ff origin master")
        else:
            run("git clone --depth 1 {}".format(git_url(namespace, name)))
@task   
@parallel
@roles("rlec", "rlec_master")
def install_rlec(rlec_installer):
    package_name = 'RLEC.tar'
    if not files.exists(package_name):
        put(rlec_installer, package_name)
        run('tar -xf {}'.format(package_name))
        sudo('./install.sh -y')
    sudo('mkdir -p {} && chown -R {}.{} {}'.format(config.rlec_datadir, config.rlec_uid, config.rlec_uid, config.rlec_datadir))



def deploy_module(module):
    resp = json.loads(run('curl -k -u "{}:{}" -F "module=@{}" https://127.0.0.1:9443/v1/modules'.format(
        config.rlec_user, config.rlec_password, module)))
    return resp['uid']

def rladmin(cmd):
    sudo('/opt/redislabs/bin/rladmin ' + cmd)

@task
@roles("rlec_master")
def create_database(db_name, num_shards, max_memory, replication):

    rladmin('tune cluster default_shards_placement sparse')
    if not files.exists(module_file):
        puts(yellow("We need to download the latest version of the module now..."))
        get_module()
    
    coord_uid = deploy_module(module_file)
    run("""curl -k -X POST -u "{rlec_user}:{rlec_pass}" -H "Content-Type: application/json" \
        -d '{{ "name": "{db_name}", "replication":{replication}, "sharding":true, "shards_count":{num_shards}, "version": "4.0", "memory_size": {mem_size}, "type": "redis", \
        "module_list":["{coord_uid}"], "module_list_args":["PARTITIONS {num_partitions} TYPE redislabs"] }}' \
        https://127.0.0.1:9443/v1/bdbs""".format(rlec_user=config.rlec_user, rlec_pass=config.rlec_password, db_name=db_name,
        num_shards=num_shards, num_partitions=num_shards, mem_size=int(max_memory)*1000000000, 
        coord_uid=coord_uid, replication='true' if replication else 'false'))
    
    puts(green("Successfully created database with {} shards!".format(num_shards)))



def download_http(url, dest):
    run('curl -# -o {} {}'.format(dest, url))

@task
@roles("rlec_master")
def get_module():
    download_http(
                'https://redismodules.s3.amazonaws.com/rscoordinator/rscoordinator.Linux-x86_64.latest.zip', 
                module_file)
    
  

@roles("rlec_master")
def upload_modules(rscoord_mod):
    """
    Upload the modules from local machine to the target machine
    """

    if rscoord_mod:
        put(rscoord_mod, module_file)
  


@task
@runs_once
@roles("rlec_master")
def create_cluster(cluster_name, license_file):
    put(license_file, 'license.txt')
    rladmin("cluster create name {} username \"{}\" password \"{}\" persistent_path \"{}\" license_file \"license.txt\"".format(
        cluster_name, config.rlec_user, config.rlec_password, config.rlec_datadir))

@task
@serial
@roles("rlec")
def join_rlec(cluster_host):
    ip = resolve(cluster_host)
    rladmin("cluster join nodes \"{}\" username \"{}\" password \"{}\" persistent_path \"{}\"".format(
        ip, config.rlec_user, config.rlec_password, config.rlec_datadir
    ))

@task
@parallel
@roles("rlec", "rlec_master")
def install_redis():

    if not files.exists('/usr/local/bin/redis-server'):
        run('wget https://github.com/antirez/redis/archive/unstable.zip && unzip -u unstable.zip')

        with cd('redis-unstable'):
            run('make -j4 all')
            sudo('make install')
    else:
        print("Redis already installed")

def module_path(mod):
    return mod
    


def get_local_ip():
    return run('host `hostname` | cut -d " " -f 4')

def resolve(host):
    return run('host {} | cut -d " " -f 4'.format(host))


@task
def upgrade_module(bdb_uid, module):
    # overrides bdb's module list with the one provided.
    # TODO: retrieve BDB's module list and update instead of overriding.
    run("""curl -k -X PUT -u "{rlec_user}:{rlec_pass}" -H "Content-Type: application/json" \
        -d '{ "module_list": {module_list} }' \
        https://127.0.0.1:9443/v1/bdbs/{uid}""".format(rlec_user=config.rlec_user, rlec_pass=config.rlec_password,
        module_list=json.dumps(module_list), uid=bdb_uid))

@task
def deploy_rlec():
    execute(install_essentials)
    execute(install_redis)
    execute(install_rlec)

@task
def download_modules():
    execute(get_modules)


