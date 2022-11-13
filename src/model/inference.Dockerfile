FROM public.ecr.aws/lambda/python:3.8

RUN pip3 install torch --extra-index-url https://download.pytorch.org/whl/cpu

COPY inference.py utils.py  ./

CMD [ "inference.lambda_handler" ]