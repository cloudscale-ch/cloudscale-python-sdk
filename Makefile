.PHONY: install lint format test coverage build clean release test-release

install:
	uv sync

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

coverage:
	uv run pytest --cov=cloudscale

build: clean
	uv build

clean:
	rm -rf dist build *.egg-info

test-release: build
	uv publish --publish-url https://test.pypi.org/legacy/

release: build
	uv publish
