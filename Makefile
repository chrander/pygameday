clean:
	rm -rf build dist pygameday.egg-info .eggs

dist: clean
	python3 setup.py sdist bdist_wheel

upload-test: dist
	# Upload to TestPyPi
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

install-test:
    # Install from TestPyPi
	pip install --index-url https://test.pypi.org/simple/ --no-deps pygameday

upload: dist
	# Upload to PyPi
	python3 -m twine upload dist/*

install:
    # Install from PyPi
	pip install pygameday

