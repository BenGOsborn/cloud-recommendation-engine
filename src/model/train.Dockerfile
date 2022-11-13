FROM public.ecr.aws/lambda/python:3.8

RUN pip3 install torch --extra-index-url https://download.pytorch.org/whl/cpu

COPY train.py utils.py  ./

CMD [ "train.lambda_handler" ]