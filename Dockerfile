FROM python:3.12-slim

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY src /src

WORKDIR /src

RUN python manage.py collectstatic --noinput

ENV DJANGO_DEBUG_FALSE=Yes

RUN adduser --uid 1234 user
USER user

CMD ["gunicorn", "--bind", ":8888", "superlists.wsgi:application"]