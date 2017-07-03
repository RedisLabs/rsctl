# rsctl

RediSearch Enterprise Distributed Search control utility

# About

This package contains scripts to help administration and set-up of RedisLabs enterprise cluster, with the enterprise distributed version of RediSearch.

It is invoked via a single command - `rsctl`, that connects to a remote server and configures redis clusters on it. It is intended to run remotely and connect to the master Redis Pack server via SSH.

# Installing rsctl

```sh
$ git clone https://github.com/RedisLabs/rsctl
$ cd rsctl
$ sudo python setup.py install
```

# Note on SSH Login

If you have a key pair for SSH login to the server, it can be specified with the `--pem` option or the `SSH_PEM` environment variable. 

If it is not given, we use the default ssh key pair as if connecting to the server with ssh with no extra arguments.

# Note on Redis Pack Credentials

You need to provide the commands with Redis Pack (Redis Labs Enterprise Cluster) login credentials.

These are the email and password you set when creating the cluster.

---

# Using rsctl to configure a RedisLabs Enterprise RediSearch Cluster

### 0. Install and configure Redis Pack cluster

The steps for that are not detailed in this scope. We assume you have a cluster ready with a version that supports modules. 

Rsctl can automate this with the commands `rsctl bootstrap_machine` and `rsctl create_cluster`.

### 1. Downloading the module

The module package is stored on a public AWS S3 bucket.

```sh
$ rsctl get_module
```

This downloads the **latest version** of  the  module **to the destination machine**, but does not install it yet.

**NOTE:** If the server does not have access to the outside world, you can download the module manually and upload it:

```sh
$  curl -o rscoordinator.zip https://redismodules.s3.amazonaws.com/rscoordinator/rscoordinator.Linux-x86_64.latest.zip
$  rsctl upload_module rscoordinator.zip
```

### 2. Create the database with the 

You need to provide:
1. The desired database name.
2. The number of shards.
3. The maxmimum memory allowance

Example:

```sh
$ rsctl create_db
# Interactive Prompt Below
> Host Name ($SSH_HOST): 1.2.3.4
> SSH User ($SSH_USER) [redis]:
> Redis Pack Login Email ($RL_USER) [user@example.com]:
> Redis Pack Password ($RL_PASS):
> Redis Pack data dir ($RL_DATADIR) [/mnt/data]:
> Database Name [mydb]:
> Number of Search Partitions (Shards) [3]:
> Database Memory Limit (in GB) [4]: 15
> Enable Replication [y/N]: n
[1.2.3.4] Executing task 'create_database'
....
$
```

---

# Full Sub-Command Documentation and options

rsctl is invoked by running

```sh
$ rsctl [OPTIONS] COMMAND [ARGS]
```

Belowe are the available commands and options for `rsctl`. All options

## Global Options

For all commands, the options below should be filled, and have corresponding environment variables (See below). 

Options are provided either via environment variables, command-line arguments, or interactive prompt. If neither an environment variable nor a command-line argument are present, the user will be prompted for the option.

### The global options are as follows:

| Command Line | Env. Var | Description | Default |
|---|---|---|---|
|  --pem | SSH_PEM | Optional .pem file for ssh connections | n/a |
| --host | SSH_HOST|   Master Redis Pack IP Address | n/a |
| --user | SSH_USER |  SSH Login User | redis |
|  --rl_user | RL_USER |   Redis Pack User Name | user@example.com |
| --rl_password | RL_PASS | Redis Pack Password | n/a |
| --rl_datadir | RL_DATADIR | Redis Pack Data storage dir | /mnt/data |


# rsctl bootstrap_machine

Bootstraps a new Redis Pack/RediSearch maching and install the essential stuff.

Options:

``` 
   --rlec_installer
   
     Path to Redis Pack installation .tar file on the local machine. It gets uploaded to the target machine.
```
# rsctl create_cluster

Creates a new Redis Pack cluster

Options:
```
  --name TEXT          
    
    Cluster Name
  
  --license_file TEXT  
    
    LICENSE file path on the local machine (gets uploaded)
```

# rsctl get_module

Downloads the coordinated search module from AWS S3. 

# rsctl upload_module {module-file.zip}

Upload module package from the local machine to the server. Use this instead of get_module when you do not have access to the S3 bucket where the module is stored.

Options:
```
  module name: 
    
    Positional argument (must follow the command name). e.g.:

    rsctl upload_module rscoordinator.zip
```

# rsctl create_db

Creates a new database with the module loaded

Options

```
 --name TEXT       
    
    Database Name

  --shards INTEGER  
    
    Number of Search Partitions (Shards)

  --maxmemory TEXT  
  
    Database Memory Limit (in GB)

  --replication     
    If set, replication is enabled
```