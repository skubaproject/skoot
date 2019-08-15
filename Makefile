all: build

build:
	docker build -t skoot .

clean:
	rm -rf yaml

cleanimage:
	docker image rm -f skoot

push:
	docker build -t quay.io/skupper/skoot:latest .
	docker push quay.io/skupper/skoot:latest

.PHONY: build cleanimage clean push run
