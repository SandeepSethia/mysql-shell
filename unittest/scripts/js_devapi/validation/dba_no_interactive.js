//@ Session: validating members
|Session Members: 14|
|createCluster: OK|
|deleteSandboxInstance: OK|
|deploySandboxInstance: OK|
|getCluster: OK|
|help: OK|
|killSandboxInstance: OK|
|resetSession: OK|
|startSandboxInstance: OK|
|checkInstanceConfiguration: OK|
|stopSandboxInstance: OK|
|dropMetadataSchema: OK|
|configureLocalInstance: OK|
|verbose: OK|
|rebootClusterFromCompleteOutage: OK|

//@# Dba: createCluster errors
||Invalid number of arguments in Dba.createCluster, expected 1 to 2 but got 0
||Argument #1 is expected to be a string
||Dba.createCluster: The Cluster name cannot be empty
||Argument #2 is expected to be a map
||Invalid values in the options: another, invalid
||Invalid value for memberSslMode option. Supported values: AUTO,DISABLED,REQUIRED.
||Invalid value for memberSslMode option. Supported values: AUTO,DISABLED,REQUIRED.
||Cannot use memberSslMode option if adoptFromGR is set to true.
||Cannot use memberSslMode option if adoptFromGR is set to true.
||Cannot use memberSslMode option if adoptFromGR is set to true.
||Invalid value for ipWhitelist, string value cannot be empty.

//@# Dba: createCluster succeed
|<Cluster:devCluster>|

//@# Dba: createCluster already exist
||Dba.createCluster: Cluster is already initialized. Use Dba.getCluster() to access it

//@# Dba: checkInstanceConfiguration errors
||Dba.checkInstanceConfiguration: Missing password for 'root@localhost:<<<__mysql_sandbox_port1>>>'
||Dba.checkInstanceConfiguration: Missing password for 'sample@localhost:<<<__mysql_sandbox_port1>>>'
||Dba.checkInstanceConfiguration: The instance 'root@localhost:<<<__mysql_sandbox_port1>>>' is already part of an InnoDB Cluster

//@ Dba: checkInstanceConfiguration ok1
|ok|

//@ Dba: checkInstanceConfiguration ok2
|ok|

//@ Dba: checkInstanceConfiguration ok3
|ok|

//@<OUT> Dba: checkInstanceConfiguration report with errors
{
    "config_errors": [
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "binlog_checksum",
            "required": "NONE"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "binlog_format",
            "required": "ROW"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "disabled_storage_engines",
            "required": "MyISAM,BLACKHOLE,FEDERATED,CSV,ARCHIVE"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "enforce_gtid_consistency",
            "required": "ON"
        },
        {
            "action": "config_update",
            "current": "OFF",
            "option": "gtid_mode",
            "required": "ON"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "log_bin",
            "required": "<no value>"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "log_slave_updates",
            "required": "ON"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "master_info_repository",
            "required": "TABLE"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "relay_log_info_repository",
            "required": "TABLE"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "report_port",
            "required": "<<<__mysql_sandbox_port2>>>"
        },
        {
            "action": "config_update",
            "current": "<not set>",
            "option": "transaction_write_set_extraction",
            "required": "XXHASH64"
        }
    ],
    "errors": [],
    "restart_required": false,
    "status": "error"
}


//@# Dba: configureLocalInstance errors
||Dba.configureLocalInstance: This function only works with local instances
||Dba.configureLocalInstance: Missing password for 'root@localhost:<<<__mysql_sandbox_port1>>>'
||Dba.configureLocalInstance: Missing password for 'sample@localhost:<<<__mysql_sandbox_port1>>>'
||Dba.configureLocalInstance: The path to the MySQL Configuration is required to verify and fix the InnoDB Cluster settings

//@<OUT> Dba: configureLocalInstance updating config file
{
    "status": "ok"
}

//@<OUT> Dba: configureLocalInstance report fixed 1
{
    "status": "ok"
}

//@<OUT> Dba: configureLocalInstance report fixed 2
{
    "status": "ok"
}
//@<OUT> Dba: configureLocalInstance report fixed 3
{
    "status": "ok"
}


//@# Dba: getCluster errors
||Invalid cluster name: Argument #1 is expected to be a string
||Invalid number of arguments in Dba.getCluster, expected 0 to 1 but got 2
||Dba.getCluster: The Cluster name cannot be empty

//@ Dba: getCluster
|<Cluster:devCluster>|
