# Elbow

Simple Crowdfunding


## Tests

```
./manage.py test
```


## Setup SCSS

Edit the elbow/apps/public/static/css/_theme.scss and replace the variables with something you like.

```
./manage.py bower install

vim bower_components/bootstrap-sass/assets/stylesheets/bootstrap/_bootstrap/_variables.scss

# on line: 8, replace
@import "bootstrap/mixins";
# with
@import "../../../../elbow/apps/public/static/css/theme";

```

You could use: http://www.lavishbootstrap.com/ and copy paste the variables



## Setup translations


```
tx set --auto-local -r elbow.djangopo 'locale/<lang>/LC_MESSAGES/django.po' \
--source-lang en --type PO --source-file locale/en/LC_MESSAGES/django.po
```

will output

```
Only printing the commands which will be run if the --execute switch is specified.

tx set --source -r elbow.djangopo -l en locale/en/LC_MESSAGES/django.po

tx set -r elbow.djangopo -l de locale/de/LC_MESSAGES/django.po
tx set -r elbow.djangopo -l en locale/en/LC_MESSAGES/django.po
```


## Update secupay IBAN data

```
my_hash = 'bkrmrgnonlyu967461'  # Get a current Order secupay hash
data = Order.SECUPAY.payment().status(hash=my_hash)
import json
json.loads(data)
```