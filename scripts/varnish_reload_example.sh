#!/bin/bash
name=`date +%H%M%S`
varnishadm vcl.load ${name} /etc/varnish/default.vcl && varnishadm vcl.use ${name}

