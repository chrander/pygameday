clean:
	rm -rf build dist pygameday.egg-info .eggs

dist: clean
	uv build

upload-test: dist
	uv run twine upload --repository-url https://test.pypi.org/legacy/ dist/*

install-test:
	pip install --index-url https://test.pypi.org/simple/ --no-deps pygameday

upload: dist
	uv run twine upload dist/*

install:
	uv sync
