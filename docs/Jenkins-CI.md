# Design of Jenkins Service Runner

Jenkins itself is not designed to supervise long-running services. Instead, it
should be used to invoke such a supervisor. In the case of the Lassa development
environment, Systemd is used to run the latest version of the service. Jenkins
is responsible for installing the College-JUMP website and restarting the
unit.

## User/Group Permissions

Create a new UNIX system group called `collegejumpadmin` and add the `jenkins`
user to it. Seeing those changes will probably require restarting the Jenkins
service.

## Sudoers Modifications

Add a file with the following contents at the path `/etc/sudoers.d/collegejump`
to allow members of the `collegejumpadmin` group to perform the appropriate
actions. (Note, this includes unbridled access to `systemctl` and `pip3`, which
could be easily leveraged for full system compromise.)

```
# Allow members of collegejumpadmin to install and restart the College-JUMP Website
%collegejumpadmin ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/bin/pip3
```

## Unit File Installation

The Unit file from the repository must be linked in. This is accomplished by
running `systemctl link contrib/collegejump.service`.
