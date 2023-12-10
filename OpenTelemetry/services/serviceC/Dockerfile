FROM python:3.12-alpine
WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN pip install pipenv && \
    pipenv install --deploy --ignore-pipfile
COPY . /app
EXPOSE 5001
CMD ["pipenv", "run", "python", "service_c.py"]
