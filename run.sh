#!/usr/bin/env bash
gunicorn -w 4 -b 127.0.0.1:7080 autoapp:app