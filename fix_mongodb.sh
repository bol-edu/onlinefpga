docker rm -f boledudb
docker run --rm -v /mnt/LabData/hls00/boledudb/:/data/db --name boledudb-repair mongo:6.0.1 mongod --repair