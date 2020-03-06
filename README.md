## PTT_web_crawler
### 使用方法：
* Docker:
1. download and install Docker desktop of [Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac/) or [Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)

2. clone this repo and cd into this as working directory

3. build image from `Dockerfile` and run `ptt_web_crawler_docker.py` in container:
```
docker build -t my_image .
docker run --mount type=bind,source={/YOUR/PATH/OF/LOCAL/WORKING/DIRECTORY},target=/work_dir my_image python3 /work_dir/ptt_web_crawler_docker.py -Board_Name {看板名稱} -Scrap_Page {爬取頁數}
```

* linux or terminal:
1. clone this repo and cd into this as working directory

2. install the required packages in [requirements.txt](https://github.com/pcchencode/PTT_web_crawler/blob/master/requirements.txt)

3. command
```
python3 ptt_web_crawler.py -Board_Name {欲爬取看板} -Scrap_Page {欲爬取頁數}
```

