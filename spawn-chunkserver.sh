cd $(dirname $0)
cd master
docker build -t qfs-chunkserver .
docker run -d --rm \
	--name "qfs-chunkserver-$2" \
	-p "$1":8000 \
	qfs-master
