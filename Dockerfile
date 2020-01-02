FROM python:3.7-alpine
WORKDIR /code
ENV FLASK_APP main.py
ENV FLASK_RUN_HOST 0.0.0.0
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps libffi-dev gcc musl-dev postgresql-dev && \
 apk add zlib-dev jpeg-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apk --purge del .build-deps
COPY . .
CMD ["flask", "run"]
