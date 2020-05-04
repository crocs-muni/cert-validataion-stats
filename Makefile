interpret = python3.6

install:
	$(interpret) setup.py install

user_install:
	$(interpret) setup.py install --user

test:
	$(interpret) -m unittest discover -s tests -v
	rm -rf tests/test_storage

clear:
	rm -rf build/
	rm -rf dist/
	rm -rf cevast.egg-info/

.PHONY: install user_install test
