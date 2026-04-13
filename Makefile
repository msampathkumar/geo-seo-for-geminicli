# Requirements
# 1. Ensure that `make` utility in avaible
# 2. Ensure that this file name is `Makefile`
# 3. Ensure that this file uses only tabs as prefix & not spaces

# Setting Version
APP_VERSION=0.34


help:	## Help Command
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

version: ## Prints the Application Version
	@echo "Application Version: $(APP_VERSION)"

setup-tests: ## Test the fetch_page.py tool by fetching a page
	@echo "Testing fetch_page.py..."
	@set -e; \
	python scripts/fetch_page.py https://a2a-protocol.org/latest/ > /dev/null || (echo "Error: fetch_page.py failed to fetch the page!" && exit 1)
	@echo "Success: fetch_page.py is working."

tests: setup-tests ## Run all tests

install: ## Install the GEO skill and agents
	@echo "Running install.sh..."
	./install.sh

uninstall: ## Uninstall the GEO skill and agents
	@echo "Running uninstall.sh..."
	./uninstall.sh
