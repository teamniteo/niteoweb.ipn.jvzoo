# convenience makefile to boostrap & run buildout
# use `make options=-v` to run buildout with extra options

version = 2.7
python = bin/python
options =

all: docs tests

coverage: htmlcov/index.html

htmlcov/index.html: src/niteoweb/ipn/jvzoo/*.py bin/coverage
	@bin/coverage run --source=./src/niteoweb/ipn/jvzoo --branch bin/test
	@bin/coverage html -i --fail-under 98
	@touch $@
	@echo "Coverage report was generated at '$@'."

.installed.cfg: bin/buildout buildout.cfg buildout.d/*.cfg setup.py
	bin/buildout $(options)

bin/buildout: $(python) buildout.cfg bootstrap.py
	$(python) bootstrap.py
	@touch $@

$(python):
	virtualenv-$(version) --no-site-packages .
	@touch $@

tests: .installed.cfg
	@bin/test
	@bin/flake8 src/niteoweb/ipn/jvzoo
	@for pt in `find src/niteoweb/ipn/jvzoo -name "*.pt"` ; do bin/zptlint $$pt; done
	@for xml in `find src/niteoweb/ipn/jvzoo -name "*.xml"` ; do bin/zptlint $$xml; done
	@for zcml in `find src/niteoweb/ipn/jvzoo -name "*.zcml"` ; do bin/zptlint $$zcml; done

clean:
	@rm -rf .installed.cfg bin parts develop-eggs \
		src/niteoweb.ipn.jvzoo.egg-info lib include .Python

.PHONY: all tests clean
