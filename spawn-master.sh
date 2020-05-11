cd $(dirname $0)
docker build -t qfs-master master/.
docker run -d --rm \
	--name qfs-master \
	-p "$1":8000 \
	qfs-master
