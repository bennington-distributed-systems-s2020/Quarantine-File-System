cd $(dirname $0)
cd chunkserver
docker build -t qfs-chunkserver .
docker run -d --rm \
	--name "qfs-chunkserver-$2" \
	-p "$1":8000 \
	qfs-chunkserver
