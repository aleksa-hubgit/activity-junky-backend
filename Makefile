SERVICES = $(shell for dir in */ ; do echo $${dir%/}; done)


.PHONY: $(SERVICES) all

all: $(SERVICES)


$(SERVICES):
	docker image build -t aleksastevas/$@ ./$@

up:
	docker compose -f docker-compose-dev.yml up

down:
	docker compose -f docker-compose-dev.yml down

restart:
	docker compose -f docker-compose-dev.yml down
	docker compose -f docker-compose-dev.yml up

down-volumes:
	docker compose -f docker-compose-dev.yml down --volumes -t 3