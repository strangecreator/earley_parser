default: test

install:
	pip install -r requirements.txt

test:
	pytest tests/main.py

.PHONY: test