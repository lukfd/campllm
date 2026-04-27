up:
	docker compose up -d chroma

restart:
	docker compose restart chroma

down:
	docker compose stop chroma

clean:
	docker compose down -v
	rm -rf chroma-data

