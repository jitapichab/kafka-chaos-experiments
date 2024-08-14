# Makefile

# Variables
DB_HOST ?= localhost
BOOSTRAP_SERVERS ?= localhost:9092
ARGO_WORKFLOWS_VERSION ?= v3.5.8

# List of manifests in the manifests directory
MANIFEST_DIR = manifests
MANIFESTS = $(MANIFEST_DIR)/detective-pikachu.yaml $(MANIFEST_DIR)/order-reversed.yaml $(MANIFEST_DIR)/order-updater.yaml $(MANIFEST_DIR)/poke-order-api.yaml

# Target to install Argo Workflows and create a token
install-argo:
	@echo "Installing Argo Workflows"
	kubectl create namespace argo || true
	kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/quick-start-minimal.yaml

# Target to deploy manifests
deploy: $(MANIFESTS)
	@echo "Deploying manifests with DB_HOST=$(DB_HOST) and BOOSTRAP_SERVERS=$(BOOSTRAP_SERVERS)"
	@for manifest in $(MANIFESTS); do \
		sed -e "s/DB_HOST_SED/$(DB_HOST)/g" \
			-e "s/BOOSTRAP_SERVERS_SED/$(BOOSTRAP_SERVERS)/g" \
			$$manifest | kubectl -n default apply -f - ; \
	done

poke-order-api:
	@echo "Setting up port forwarding to Poke Order API"
	kubectl -n default port-forward service/poke-order-api-svc 8000:8000

argo-server:
	@echo "Setting up port forwarding to Argo Workflows server"
	kubectl -n argo port-forward service/argo-server 2746:2746

# Clean up target (optional)
clean:
	@echo "Cleaning up deployed resources"
	@for manifest in $(MANIFESTS); do \
	    echo "Deleting $$manifest" ; \
		kubectl delete -f $$manifest -n default; \
	done
#kubectl delete namespace argo --ignore-not-found

.PHONY: deploy install-argo clean
