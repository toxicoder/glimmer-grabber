from .celery_app import celery_app

if __name__ == '__main__':
    # Start the Celery worker
    # The '-A' flag specifies the application instance to use
    # The 'worker' command starts the worker process
    # The '-l info' flag sets the logging level to info
    celery_app.worker_main(argv=['worker', '-l', 'info'])
