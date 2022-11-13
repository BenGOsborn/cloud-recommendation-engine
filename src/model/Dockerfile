FROM public.ecr.aws/lambda/python:3.8

RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu

COPY app.py utils.py  ./

CMD [ "app.lambda_handler" ]