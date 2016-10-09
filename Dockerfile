FROM resin/rpi-raspbian:jessie

MAINTAINER Eugene Bagdasaryan <ebagdasa@cs.cornell.edu>

RUN apt-get update && \
apt-get install -y postgresql postgresql-contrib


ENTRYPOINT postgres

