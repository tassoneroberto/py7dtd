.PHONY: build-package publish

build-package:
	py -m pip install build twine
	py -m build
	py -m twine check dist/*

publish:
	twine upload dist/*
