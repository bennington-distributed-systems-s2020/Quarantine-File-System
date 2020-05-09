cd $(dirname $0)
cd master
docker build -t qfs-master .
docker run -d --rm \
	--name qfs-master \
	-p "$1":8000 \
	qfs-master
