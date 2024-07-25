# Makefile

# Variables
DB_HOST ?= localhost
BOOSTRAP_SERVERS ?= localhost:9092
ARGO_WORKFLOWS_VERSION ?= v3.5.8

# List of manifests in the manifests directory
MANIFEST_DIR = manifests
MANIFESTS = $(MANIFEST_DIR)/detective-pikachu.yaml $(MANIFEST_DIR)/order-reversed.yaml $(MANIFEST_DIR)/order-updater.yaml $(MANIFEST_DIR)/poke-order-api.yaml


# Target to deploy manifests
deploy: $(MANIFESTS)
	@echo "Deploying manifests with DB_HOST=$(DB_HOST) and BOOSTRAP_SERVERS=$(BOOSTRAP_SERVERS)"
	@for manifest in $(MANIFESTS); do \
		sed -e "s/DB_HOST_SED/$(DB_HOST)/g" \
			-e "s/BOOSTRAP_SERVERS_SED/$(BOOSTRAP_SERVERS)/g" \
			$$manifest | kubectl apply -f - ; \
	done

# Target to install Argo Workflows and create a token
install-argo:
	@echo "Installing Argo Workflows"
	kubectl create namespace argo || true
	kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/quick-start-minimal.yaml
	@echo "Creating Argo Workflows token"
	kubectl create sa argo-workflows-sa -n argo
	kubectl create clusterrolebinding argo-workflows-sa-binding --clusterrole=admin --serviceaccount=argo-workflows:argo-workflows-sa
	@ARGO_TOKEN=$$(kubectl create token argo-workflows-sa -n argo) && echo "Argo Workflows token: $$ARGO_TOKEN"

argo-server:
	@echo "Setting up port forwarding to Argo Workflows server"
	kubectl -n argo port-forward service/argo-server 2746:2746

# Clean up target (optional)
clean:
	@echo "Cleaning up deployed resources"
	@for manifest in $(MANIFESTS); do \
		kubectl delete -f $$manifest --ignore-not-found ; \
	done
	kubectl delete namespace argo-workflows --ignore-not-found

.PHONY: deploy install-argo-workflows clean