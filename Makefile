# Some simple testing tasks (sorry, UNIX only).

flake:
	pep8 aiohttp_mako tests
	pyflakes aiohttp_mako tests

test: flake
	py.test -s -v ./tests/

vtest:
	py.test -s -v ./tests/

cov cover coverage: flake
	py.test -s -v  --cov-report term --cov-report html --cov aiohttp_mako ./tests
	@echo "open file://`pwd`/htmlcov/index.html"

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover

doc:
	make -C docs html
	@echo "open file://`pwd`/docs/_build/html/index.html"

.PHONY: all build venv flake test vtest testloop cov clean doc
