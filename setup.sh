#!/bin/sh -e
# This script will check out and install Open Streaming Platform (OSP)
# It needs to be run as root in order to install packages.
# This script has been extensively tested with Ubuntu 20.04
cd $HOME

# We just need to install nginx
export DEBIAN_FRONTEND=noninteractive
apt install -yq git dialog wget

# Instructions: https://wiki.openstreamingplatform.com/Install/Standard
git clone https://gitlab.com/Deamos/flask-nginx-rtmp-manager.git
cd flask-nginx-rtmp-manager
if [ -f $HOME/noninteractive.patch ]; then
        echo "Patching osp-config.sh to be non-interactive"
        patch < $HOME/noninteractive.patch
fi
echo -n "Installing OSP"; date
export OSP_EJABBERD_SITE_ADDRESS=`hostname -f`
bash osp-config.sh install osp
echo -n "Done installing OSP"; date

# Update configs
secret=`dd if=/dev/urandom bs=16 count=1 2>/dev/null | base64 | sed 's|/|_|'`
sed -ie "0,/CHANGEME/s/CHANGEME/$secret/" /opt/osp/conf/config.py
pw=`dd if=/dev/urandom bs=16 count=1 2>/dev/null | base64 | sed 's|/|_|'`
sed -ie "0,/CHANGEME/s/CHANGEME/$pw/" /opt/osp/conf/config.py
# Restart the service
systemctl restart osp.target


# Set up letsencrypt
apt-get install -y python3-certbot-nginx certbot # install certbot
umask 022
mkdir /var/certbot
echo 'location /.well-known {
            root /var/certbot;
    }' > /usr/local/nginx/conf/locations/well-known.conf
systemctl restart nginx-osp
# If we already have recent certs, this will detect that and avoid a re-pull
certbot certonly --webroot -w /var/certbot -d `hostname -f` --email "admin@`hostname -d`" -n

# Now we set up the config for the web server
echo -n 'server {
     listen 80;
     server_name _;
     return 301 https://$host$request_uri;
}

server {
  listen 443 ssl http2 default_server;
  server_name _;

  ssl_certificate /etc/letsencrypt/live/' > /usr/local/nginx/conf/custom/osp-custom-serversredirect.conf
echo "`hostname -f`/fullchain.pem;" >> /usr/local/nginx/conf/custom/osp-custom-serversredirect.conf
echo -n '  ssl_certificate_key /etc/letsencrypt/live/' >> /usr/local/nginx/conf/custom/osp-custom-serversredirect.conf
echo "`hostname -f`/privkey.pem;" >> /usr/local/nginx/conf/custom/osp-custom-serversredirect.conf
echo '
  # set client body size to 16M #
  client_max_body_size 16M;

  include /usr/local/nginx/conf/locations/*.conf;

  # redirect server error pages to the static page /50x.html
  error_page   500 502 503 504  /50x.html;
  location = /50x.html {
      root   html;
  }
}' >> /usr/local/nginx/conf/custom/osp-custom-serversredirect.conf
systemctl restart nginx-osp



# Now that we have TLS, run through the inital wizard setup
admin_pw=`dd if=/dev/urandom bs=16 count=1 2>/dev/null | base64 | sed 's|/|_|'`
echo "$admin_pw" > ~/osp-admin.password
curl -X POST --data-urlencode "username=admin" \
        --data-urlencode "email=admin@`hostname -d`" \
        --data-urlencode "password1=$admin_pw" \
        --data-urlencode "password2=$admin_pw" \
        --data-urlencode "serverName=`hostname -f`" \
        --data-urlencode "siteProtocol=https%3A%2F%2F" \
        --data-urlencode "serverAddress=`hostname -f`" \
        --data-urlencode "recordSelect=on" \
        --data-urlencode "uploadSelect=on" \
        --data-urlencode "adaptiveStreaming=on" \
        --data-urlencode "showEmptyTables=on&allowComments=on" \
        --data-urlencode "smtpSendAs=noreply@`hostname -d`" \
        --data-urlencode "smtpAddress=mail.`hostname -d`" \
        --data-urlencode "smtpPort=25" \
        --data-urlencode "smtpUser=" \
        --data-urlencode "smtpPassword=" \
        --data-urlencode "smtpTLS=on" https://`hostname -f`/settings/initialSetup
# Some services to fail to start, so we detect this and restart them automatically
# https://gitlab.com/Deamos/flask-nginx-rtmp-manager/-/issues/411
failed_services=`systemctl --state=failed --no-pager | grep osp | cut -f 2 -d ' '`
for s in $failed_services; do
        systemctl restart $s
done

# Due to a bug, the server will throw error 500s unless osp.target is
# restarted.  https://gitlab.com/Deamos/flask-nginx-rtmp-manager/-/issues/413
systemctl restart osp.target
