sudo docker build -t marvel .
sudo docker run -it --rm -v `pwd`:/mnt/mydata/ marvel
