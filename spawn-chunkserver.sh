cd $(dirname $0)
docker build -t qfs-chunk chunkserver/.
docker run -d --rm \
	--name "qfs-chunk-$2" \
	-p "$1":8000 \
	qfs-chunk
