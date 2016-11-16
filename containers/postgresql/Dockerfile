FROM resin/rpi-raspbian:jessie-20160831

MAINTAINER Eugene Bagdasaryan <ebagdasa@cs.cornell.edu>

ENV PG_MAJOR 9.4
#ENV LANG en_US.utf8
ENV PATH /usr/lib/postgresql/${PG_MAJOR}/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV PGDATA /var/lib/postgresql/data

## Prerequisites

RUN apt-get update && apt-get install -y --no-install-recommends curl locales postgresql-common\
 && sed -ri 's/#(create_main_cluster) .*$/\1 = false/' /etc/postgresql-common/createcluster.conf\
 && apt-get install -y --no-install-recommends postgresql-${PG_MAJOR} postgresql-contrib\
 && gpg --keyserver pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4\
 && cd /usr/local/bin\
 && for suffix in "" ".asc"; do \
     curl -kLSo gosu${suffix}\
       "https://github.com/tianon/gosu/releases/download/1.3/gosu-$(dpkg --print-architecture)${suffix}"; \
   done \
 && gpg --verify gosu.asc\
 && rm gosu.asc\
 && chmod +x gosu\
 && apt-get purge -y --auto-remove curl\
 && apt-get clean && rm -rf /var/lib/apt/lists/*\


VOLUME /var/lib/postgresql/data
COPY entrypoint.sh /

EXPOSE 5432
