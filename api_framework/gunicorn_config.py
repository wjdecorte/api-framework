import os

workers = int(os.environ.get("WORKERS", 1))
worker_class = "uvicorn_worker.UvicornWorker"
bind = "0.0.0.0:9000"
