# Hosting Management System - Deployment Makefile

HOST ?= asterra.remoteds.us
REMOTE_DIR ?= /opt/hosting-api
VENV ?= /opt/hosting-api/.venv
PYTHON ?= python3

.PHONY: test push deploy restart health

## Run unit tests
test:
	cd hosting-management-system && $(PYTHON) -m pytest -q

## Commit and push current changes (usage: make push m="Your message")
push:
	git add -A
	git commit -m "$(m)" || true
	git push

## Deploy to remote (rsync + install deps + restart + health check)
deploy:
	bash hosting-management-system/scripts/deploy_hosting_api.sh $(HOST) $(REMOTE_DIR) $(VENV)

## Restart remote API only (no sync)
restart:
	ssh root@$(HOST) "(systemctl restart hosting-api || true); pkill -f 'uvicorn.*5051' || true; sleep 2; cd $(REMOTE_DIR) && nohup $(VENV)/bin/uvicorn app_fastapi:app --host 0.0.0.0 --port 5051 >> /var/log/hosting-api.log 2>&1 &"

## Health check endpoints
health:
	ssh root@$(HOST) "curl -sf http://127.0.0.1:5051/health && echo && curl -sf http://127.0.0.1:5051/api/v1/kanban/health && echo"
