FROM pytorch/pytorch:1.13.0-cuda11.6-cudnn8-runtime

# Install requirements
COPY requirements.txt .

RUN pip3 install -r requirements.txt

# Copy model entrypoint and handler
COPY entrypoint.py /usr/local/bin/entrypoint.py

COPY model_handler.py /home/model-server/model_handler.py

ENTRYPOINT ["python", "/usr/local/bin/entrypoint.py"]