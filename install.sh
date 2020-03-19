#!/bin/bash

# install dependencies
if ! aws --version ; then
    echo "AWS not installed, installing"

    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install

    sudo rm -rf aws
    sudo rm -rf awscliv2.zip
fi

if ! python3 --version ; then
    sudo apt install python3
fi

if ! pip3 --version ; then
    sudo apt install python3-pip
fi

pip3 install boto3