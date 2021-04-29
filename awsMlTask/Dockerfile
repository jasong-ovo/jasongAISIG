FROM public.ecr.aws/lambda/python:3.8

RUN pip install boto3 \
    && pip install torch==1.6.0 \
    && pip install pytorchcv \
    && pip install pillow 

COPY app.py   ./
CMD ["app.handler"]
COPY utils.py ./

