up:
	docker compose up -d --build

restart:
	docker compose restart

down:
	docker compose stop

clean:
	docker compose down -v
	rm -rf chroma-data

