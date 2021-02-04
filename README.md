# HardNut

Hard Nut is simple, secure, unified multi-user database/backend. 

## Running server
~~~
export CERT=~/hardnut-certs/hardnut-fullchain.pem 
export PRIVKEY=~/hardnut-certs/hardnut-key.pem 
export SECRET=`date`
export APPS_PATH=~/hardnut-apps/
# export FLASK_ENV=development
./hardnut-server.py 
~~~

## Oauth2 / OpenID Connect

### Google

https://console.developers.google.com/apis/dashboard


## Working from CLI
~~~
curl -k -H 'Host: test.apps.hardnut.www-security.net:5000' -H 'X-API-KEY: asdf' -T asdf.txt https://localhost:5000/app/etc/asdf2.txt

curl -k -H 'Host: test.apps.hardnut.www-security.net:5000' -H 'X-API-KEY: asdf' -X DELETE https://localhost:5000/app/etc/asdf2.txt

curl -v -k -H "Content-Type: application/json"  -H 'Host: test.apps.hardnut.www-security.net:5000' -H 'X-API-KEY: asdf' -X POST -d @/tmp/post.json  https://localhost:5000/var/flags.json
~~~
