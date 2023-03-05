FROM python:latest
RUN groupadd -r -g 1337 user && useradd -r -u 1337 -g user user
USER user
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
WORKDIR /app 
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /app 
ENTRYPOINT ["python3"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]
