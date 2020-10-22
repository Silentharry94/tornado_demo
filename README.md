### Just for fun

### Like a baby

### 项目启动命令
cd $project;python3 server.py --env=$env --port=$port

### 项目更新命令
cd $project;git pull

### 异步队列启动命令(需要先启动后端服务，生成配置文件)
cd $project;celery -B -A async_task.app worker -l info -s celerybeat-schedule

