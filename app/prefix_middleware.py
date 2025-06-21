class PrefixMiddleware:
    def __init__(self, app, prefix, exclude_paths=None):
        self.app = app
        self.prefix = prefix
        self.exclude_paths = exclude_paths or []

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO', '')

        # exclude_paths 중 하나라도 path가 시작되면 미들웨어 적용하지 않고 바로 app 호출
        for exclude in self.exclude_paths:
            if path.startswith(exclude):
                return self.app(environ, start_response)

        if path.startswith(self.prefix):
            environ['PATH_INFO'] = path[len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            from werkzeug.wrappers import Response
            return Response('Not Found', status=404)(environ, start_response)
