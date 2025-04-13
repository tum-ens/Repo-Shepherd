broker_url = 'pyamqp://guest@localhost//'
result_backend = 'rpc://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Oslo'
enable_utc = True

task_routes = {
    'tasks.add': 'low-priority',
}