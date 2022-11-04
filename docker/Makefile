
# Note this makefile is not used in the CI build - this is just for building local image.

env-var-must-be-set-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

image: env-var-must-be-set-VERSION
	docker build --build-arg GOPRO_OVERLAY_VERSION=$(VERSION) \
		--tag overlaydash/gopro-dashboard-overlay:latest \
		--tag overlaydash/gopro-dashboard-overlay:v$(VERSION) \
		.
