VER=0.2.0
build:
	docker build . -t fifa-stat-extractor -t pawelflajszer/fifa-stat-extractor:${VER} -t pawelflajszer/fifa-stat-extractor:latest
run:
	docker run --mount type=bind,source=${FIFA_WORKDIR},target=/app/db/fifa pawelflajszer/fifa-stat-extractor:latest
cleanup:
	docker image rm pawelflajszer/fifa-stat-extractor:latest -f
	docker image rm pawelflajszer/fifa-stat-extractor:${VER} -f
pull:
	docker pull pawelflajszer/fifa-stat-extractor:latest
push:
	docker push pawelflajszer/fifa-stat-extractor:${VER}
	docker push pawelflajszer/fifa-stat-extractor:latest