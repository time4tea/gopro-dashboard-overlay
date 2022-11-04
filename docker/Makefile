

env-var-must-be-set-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Environment variable $* not set"; \
		exit 1; \
	fi

image: env-var-must-be-set-VERSION
	docker build --build-arg GOPRO_OVERLAY_VERSION=$(VERSION) \
		--tag overlaydash/gopro-overlay-dashboard:latest \
		--tag overlaydash/gopro-overlay-dashboard:v$(VERSION) \
		.
