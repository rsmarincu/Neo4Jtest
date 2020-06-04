FROM python:3.8.2

COPY Pipfile* /tmp/
WORKDIR /tmp/
RUN pip install pipenv
RUN pipenv install --system

COPY . /app/
WORKDIR /app/

ENTRYPOINT ["python"]
CMD ["-u", "run.py"]