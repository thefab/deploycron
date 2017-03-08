test:
	cd ./tests && nosetests

install:
	python setup.py install
	
coveralls:
	cd ./tests && nosetests --with-coverage --cover-package=deploycron

