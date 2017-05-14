# rsctl

RediSearch/RSCoordinator distributed search control utility

# About

This package contains scripts to help administration and set-up of RedisLabs enterprise cluster, with RediSearch and RSCoordinator - providing a powerful distributed search engine over Redis.

It is invoked via a single command - `rsctl`, that connects to a remote server and configures redis clusters on it. It is intended to run remotely and connect to the master RLEC server via SSH.

# Installing rsctl

```sh
$ cd /path/to/rsctl
$ sudo python setup.py install
```

---

# Using rsctl to configure a RedisLabs Enterprise RediSearch Cluster

### 0. Install and configure RLEC cluster

The steps for that are not detailed in this scope. We assume you have a cluster ready with a version that supports modules. 

Rsctl can automate this with the commands `rsctl bootstrap_machine` and `rsctl create_cluster`.

### 1. Downloading the modules

The module packages are stored on a special AWS S3 bucket. If you have access to it, use the command:

```sh
$ rsctl get_modules [--s3_accesskey {KEY} --s3_secretkey {SECRET}]
```

This downloads the **latest versions** of both modules to the destinatino machine, but does not install them yet. If the S3 credentials are not provided, you will be prompted to provide them. The AWS S3 keypair must be authorized to access the bucket where the modules are stored.

**NOTE:** If you do not have access, but have received the module package files manually, you can either upload them to the home directory of the ssh user on the server, or use the following command:

```sh
$  rsctl upload_modules --redisearch /path/to/redisearch.zip --coordinator /path/to/rscoordinator.zip
```

### 2. Create the database with the modules

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
> RLEC Login Email ($RL_USER) [user@example.com]:
> RLEC Password ($RL_PASS):
> RLEC data dir ($RL_DATADIR) [/mnt/data]:
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
| --host | SSH_HOST|   Master RLEC IP Address | n/a |
| --user | SSH_USER |  SSH Login User | redis |
|  --rl_user | RL_USER |   RLEC User Name | user@example.com |
| --rl_password | RL_PASS | RLEC Password | n/a |
| --rl_datadir | RL_DATADIR | RLEC Data storage dir | /mnt/data |


# rsctl bootstrap_machine

Bootstraps a new RLEC/RediSearch maching and install the essential stuff.

Options:

``` 
   --rlec_installer
   
     Path to RLEC installation .tar file on the local machine. It gets uploaded to the target machine.
```
# rsctl create_cluster

Creates a new RLEC cluster

Options:
```
  --name TEXT          
    
    Cluster Name
  
  --license_file TEXT  
    
    LICENSE file path on the local machine (gets uploaded)
```

# rsctl get_modules

Downloads the modules from AWS S3. 

**NOTE**: The AWS S3 keypair must be authorized to access the bucket where the modules are stored. Contact @Dvir for further details.

Options:

```
  --s3_accesskey TEXT  
  
    S3 Access Key
  
  --s3_secretkey TEXT  
    
    S3 Secret Key
```

# rsctl upload_modules

Upload module packages from the local machine to the server. Use this instead of get_modules when you do not have access to the S3 bucket where the modules are stored.

Options:
```
  --redisearch TEXT   
    
    Local RediSearch packge file path

  --coordinator TEXT  
    
    Local RSCoordinator packge file path
```

# rsctl create_db

Creates a new database with both modules loaded. 

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