FROM python:3.10.6
WORKDIR /Smell-taste-disorder-question-answering-interface

COPY . /Smell-taste-disorder-question-answering-interface
RUN pip install -r requirements.txt
COPY . /Smell-taste-disorder-question-answering-interface
CMD ["python", "app.py" ]

