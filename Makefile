all: build

build:
	docker build -t skoot .

cleanimage:
	docker image rm -f skoot

push:
	docker build -t quay.io/skupper/skoot:latest .
	docker push quay.io/skupper/skoot:latest

.PHONY: build cleanimage push run
