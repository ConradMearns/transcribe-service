# Uninstalling

To uninstall the AWS CLI version 2, run the following commands, substituting the paths you used to install.

Find the symlinks that you created in the --bin-dir folder.

$ which aws
/usr/local/bin/aws

Use that to find the --install-dir folder that the symlink points to.

$ ls -l /usr/local/bin/aws
lrwxrwxrwx 1 ec2-user ec2-user 49 Oct 22 09:49 /usr/local/bin/aws -> /usr/local/aws-cli/v2/current/bin/aws

Now delete the two symlinks in the --bin-dir folder. If your user account has write permission to these folders, you don't need to use sudo.

$ sudo rm /usr/local/bin/aws
$ sudo rm /usr/local/bin/aws2_completer

Finally, you can delete the --install-dir folder. Again, if your user account has write permission to this folder, you don't need to use sudo.

$ sudo rm -rf /usr/local/aws-cli

