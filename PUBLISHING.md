# Publishing to PyPI

## First Time Setup

1. Create a PyPI account at https://pypi.org/account/register/

2. Create an API token:
   - Go to https://pypi.org/manage/account/token/
   - Create a token with scope "Entire account"
   - Save the token (starts with `pypi-`)

3. Install build tools:
   ```bash
   pip install build twine
   ```

## Publishing Steps

1. Update version in `pyproject.toml` if needed

2. Clean old builds:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

3. Build the package:
   ```bash
   python -m build
   ```

4. Check the build (optional):
   ```bash
   twine check dist/*
   ```

5. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```
   - Enter `__token__` as username
   - Enter your API token as password

## Test on TestPyPI First (Recommended)

1. Create TestPyPI account: https://test.pypi.org/account/register/

2. Upload to TestPyPI:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

3. Test install:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ pydantic-error-handling
   ```

4. If it works, upload to real PyPI (step 5 above)

## After Publishing

Users can install with:
```bash
pip install pydantic-error-handling
```

## Version Bumping

Follow semantic versioning:
- `0.1.0` → `0.1.1` (bug fixes)
- `0.1.0` → `0.2.0` (new features, backward compatible)
- `0.1.0` → `1.0.0` (breaking changes)
