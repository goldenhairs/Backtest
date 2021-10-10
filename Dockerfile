FROM python:3

WORKDIR /root/Backtest
COPY . .
ENV CONFIG_PATH=/root/configs/config.json
ENV PYTHONPATH=$PYTHONPATH:/root/:/root/Backtest/server/pb/

RUN mkdir /root/.pip/
COPY pip.conf /root/.pip/pip.conf
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m grpc_tools.protoc \
-I ./server/pb/ \
--python_out=./server/pb/ \
--grpc_python_out=./server/pb/ \
./server/pb/backtest.proto

EXPOSE 50052

ENTRYPOINT python ./server/start.py
# ENTRYPOINT ["tail","-f","/dev/null"]