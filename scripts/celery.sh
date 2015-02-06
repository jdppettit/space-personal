#!/bin/bash

cd /srv/space
celery -A jobs worker --loglevel=INFO --detach
