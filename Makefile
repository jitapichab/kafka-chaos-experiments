# Makefile

# Variables
DB_HOST ?= localhost
BOOTSTRAP SERVERS ?= localhost:9092
ARGO_WORKFLOWS_VERSION ?= v3.5.8
# Aditional Vars to be used in the iam configuration and the chaos pod
NAMESPACE ?= kafka-chaos-experiments
PROFILE ?= iac-playground
CLUSTER_NAME ?= iac-playground
POLICY_NAME ?= msk-policy
POLICY_FILE ?= aws/msk-policy.json
SERVICE_ACCOUNT_NAME ?= kafka-chaos-experiments
AWS_REGION ?= us-west-2
MSK_CLUSTER_ARN ?= my_cluster_arn


# List of manifests in the manifests directory
MANIFEST_DIR = manifests
MANIFESTS = $(MANIFEST_DIR)/detective-pikachu.yaml $(MANIFEST_DIR)/order-reversed.yaml $(MANIFEST_DIR)/order-updater.yaml $(MANIFEST_DIR)/poke-order-api.yaml

# Script paths
IAM_SCRIPT = $(AWS_DIR)/create-iam-service-account.sh



# Target to install Argo Workflows
install-argo:
	@echo "Installing Argo Workflows"
	kubectl create namespace argo || true
	kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/${ARGO_WORKFLOWS_VERSION}/quick-start-minimal.yaml

# Target to deploy application stack
deploy: $(MANIFESTS)
	@echo "Deploying manifests with DB_HOST=$(DB_HOST) and BOOTSTRAP_SERVERS=$(BOOTSTRAP_SERVERS)"
	@for manifest in $(MANIFESTS); do \
		sed -e "s/DB_HOST_SED/$(DB_HOST)/g" \
			-e "s/BOOTSTRAP_SERVERS_SED/$(BOOTSTRAP_SERVERS)/g" \
			$$manifest | kubectl -n default apply -f - ; \
	done

# Target to set up port forwarding poke-order-api
poke-order-api:
	@echo "Setting up port forwarding to Poke Order API"
	kubectl -n default port-forward service/poke-order-api-svc 8000:8000

# Target to set up port forwarding to Argo Workflows server
argo-server:
	@echo "Setting up port forwarding to Argo Workflows server"
	kubectl -n argo port-forward service/argo-server 2746:2746

# Target to configure IAM service account
configure-iam-service-account:
	@echo "Configuring IAM service account using $(IAM_SCRIPT)"
	@chmod +x $(IAM_SCRIPT)
	@$(IAM_SCRIPT) --policy_file "file://$(POLICY_FILE)"

deploy-chaos-pod:
	@echo "Deploying Kafka Chaos Experiments Pod with AWS_PROFILE=$(PROFILE), BOOTSTRAP_SERVERS=$(BOOTSTRAP_SERVERS), MSK_CLUSTER_ARN=$(MSK_CLUSTER_ARN), AWS_REGION=$(AWS_REGION)"
	@sed \
		-e "s|{{BOOTSTRAP_SERVERS}}|$(BOOTSTRAP_SERVERS)|g" \
		-e "s|{{MSK_CLUSTER_ARN}}|$(MSK_CLUSTER_ARN)|g" \
		$(MANIFEST_DIR)/kafka-chaos-experiments.yaml kubectl -n $(NAMESPACE) apply -f - ;

# Target Clean up the application stack
clean:
	@echo "Cleaning up deployed resources"
	@for manifest in $(MANIFESTS); do \
	    echo "Deleting $$manifest" ; \
		kubectl delete -f $$manifest -n default; \
	done

# Target to remove Argo Workflows
remove-argo:
	@echo "Removing Argo Workflows"
	kubectl delete namespace argo --ignore-not-found

.PHONY: deploy install-argo clean remove-argo configure-iam-service-account deploy-chaos-pod