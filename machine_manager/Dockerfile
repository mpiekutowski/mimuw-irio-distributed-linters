FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY src /app/src

CMD ["python", "src/machine_manager.py"]