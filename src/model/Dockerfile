FROM pytorch/pytorch:1.13.0-cuda11.6-cudnn8-runtime

COPY entrypoint.py /usr/local/bin/entrypoint.py

COPY model_handler.py /home/model-server/model_handler.py

ENTRYPOINT ["python", "/usr/local/bin/entrypoint.py"]