VER=0.1.0
build:
	docker build . -t fifa-stat-extractor -t pflajszer/fifa-stat-extractor:${VER} -t pflajszer/fifa-stat-extractor:latest
run: build
	docker run --mount type=bind,source=${FIFA_WORKDIR},target=/app/db/fifa docker.io/pflajszer/fifa-stat-extractor:latest
cleanup:
	docker image rm pflajszer/fifa-stat-extractor:latest -f
	docker image rm pflajszer/fifa-stat-extractor:${VER} -f
