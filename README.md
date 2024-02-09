# Earley parser for context-free grammars on Python

## How to launch?
Run the folowing command in your cmd:
```bash
<python-executable> src/main.py -i <path-to-input-file> -o <path-to-output-file>
```

If input data is incorrect `"InputError"` will be written to the output file.

## Testing

Firstly, install `pytest`:
```bash
pip install -r requirements.txt
```

or via `make`:
```bash
make install
```

And then run tests:
```bash
pytest tests/main.py
```

or via `make`:
```bash
make test
```

## License

MIT