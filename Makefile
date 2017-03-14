test:
	cd ./tests && nosetests --exe

install:
	python setup.py install

tinstall:
	pip install -r test-requirements.txt
	python setup.py develop
	
coveralls:
	cd ./tests && nosetests --exe --with-coverage --cover-package=deploycron

coverage:
	cd ./tests && coverage run `which nosetests` --exe && coverage html --include='*/Github_peloycron/deploycron/*' --omit='test_*'
