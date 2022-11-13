FROM python:3.8

# Install requirements
COPY requirements.txt .

RUN pip3 install -r requirements.txt

# Copy model entrypoint and handler
COPY entrypoint.py /usr/local/bin/entrypoint.py

COPY model_handler.py /home/model-server/model_handler.py

ENTRYPOINT ["python", "/usr/local/bin/entrypoint.py"]