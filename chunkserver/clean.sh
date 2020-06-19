#!/bin/bash
read -p "Are you sure you want to clear all chunks and buffers? (y/n) " -r confirm
#-p prompt -r take backslashes literally
if [[ $confirm =~ ^[Yy]$ ]]
then
    rm -rfv chunk/*.chunk
    rm -rfv buffer/*.buffer
fi
