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

