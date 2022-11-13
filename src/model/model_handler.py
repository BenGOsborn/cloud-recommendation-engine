from sagemaker_inference.default_handler_service import DefaultHandlerService


class HandlerService(DefaultHandlerService):
    def __init__(self):
        super().__init__()

    # Initialize handler
    def initialize(self, context):
        print("HELLO WORLD FROM INITIALIZE", context)

        return super().initialize(context)

    # Handle an incoming request
    def handle(self, data, context):
        print("HELLO WORLD FROM HANDLE", data, context)

        return super().handle(data, context)


_service = HandlerService()


def handle(data, context):
    if not _service.initialized:
        _service.initialize(context)

    if data is None:
        return None

    return _service.handle(data, context)
