from sagemaker_inference.default_handler_service import DefaultHandlerService


class HandlerService(DefaultHandlerService):
    def __init__(self):
        super().__init__()

    # Initialize handler
    def initialize(self, context):
        return super().initialize(context)

    # Handle an incoming request
    def handle(self, data, context):
        return super().handle(data, context)
