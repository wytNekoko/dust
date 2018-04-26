#!/usr/bin/env bash
#source ../env_dust/bin/activate
gunicorn -w 4 -b 127.0.0.1:7080 autoapp:app
#--access-logfile /var/log/dust/gunicorn-access.log
#--error-logfile /var/log/dust/gunicorn-error.log autoapp:app