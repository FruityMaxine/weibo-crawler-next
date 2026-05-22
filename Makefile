# weibo-crawler-next Makefile
# 一键命令汇总. 用法: make <target>

.PHONY: help install dev-install lint test run serve tui \
        build-frontend build-binary docker docker-up docker-down \
        clean release

help:
	@echo "weibo-crawler-next — 常用命令:"
	@echo ""
	@echo "  install         以生产模式装依赖 (uv venv + pip install .)"
	@echo "  dev-install     装开发依赖含 dev/tui/mysql/postgres extras"
	@echo "  lint            ruff check + mypy"
	@echo "  test            pytest 全测"
	@echo ""
	@echo "  run UID=xxx     wcn run -u xxx -n 20"
	@echo "  serve           启 FastAPI 后端 (127.0.0.1:28800)"
	@echo "  tui             启 Textual TUI"
	@echo ""
	@echo "  build-frontend  vite build → frontend/dist"
	@echo "  build-binary    PyInstaller 单文件 binary → dist/wcn"
	@echo ""
	@echo "  docker          docker build 本地镜像"
	@echo "  docker-up       docker compose up -d"
	@echo "  docker-down     docker compose down"
	@echo ""
	@echo "  clean           删除 build/cache 产物"
	@echo "  release VERSION=0.x.y.z  打 git tag + push"

install:
	uv venv .venv --python 3.12
	uv pip install -e "." --python .venv

dev-install:
	uv venv .venv --python 3.12
	uv pip install -e ".[dev,tui,mysql,postgres,mongo]" --python .venv

lint:
	.venv/bin/ruff check backend cli tests
	.venv/bin/mypy backend cli || true

test:
	.venv/bin/pytest tests/ -v

run:
	@if [ -z "$(UID)" ]; then echo "用法: make run UID=1669879400"; exit 1; fi
	.venv/bin/wcn run -u $(UID) -n 20

serve:
	.venv/bin/wcn serve

tui:
	.venv/bin/wcn tui

build-frontend:
	cd frontend && npm ci && npm run build

build-binary:
	uv pip install pyinstaller --python .venv
	cd deploy/pyinstaller && ../../.venv/bin/pyinstaller wcn.spec --distpath ../../dist

docker:
	docker build -t weibo-crawler-next:latest .

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	rm -rf .venv/ dist/ build/ frontend/dist/ frontend/node_modules/ \
	       .pytest_cache/ .ruff_cache/ .mypy_cache/ \
	       __pycache__/ **/__pycache__/

release:
	@if [ -z "$(VERSION)" ]; then echo "用法: make release VERSION=0.4.0.0"; exit 1; fi
	git tag -a "v$(VERSION)" -m "Release v$(VERSION)"
	git push origin "v$(VERSION)"
	@echo "✓ tagged v$(VERSION), CI 会自动触发 release.yml"
