test:
	flake8 ./
	cd ./tests && nosetests --exe

install:
	python setup.py install

tinstall:
	pip install -r test-requirements.txt
	python setup.py develop
