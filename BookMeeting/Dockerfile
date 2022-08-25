FROM python:3.8

COPY . .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r BookMeeting/requirements.txt

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]