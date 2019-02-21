# pytest-jinja

This package produces HTML test reports, which allow grouping tests by metadata.

The CSS and Javascript has been taken and modified from here: https://github.com/pytest-dev/pytest-html/tree/master/pytest_html

I've used Jinja templating to simplify the generation of HTML. The context data
used to render the Jinja templates is extracted from JSON using:
https://github.com/numirias/pytest-json-report

The project I've used to generate dummy test output is here:
https://github.com/khornlund/racetest