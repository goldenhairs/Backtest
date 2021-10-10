import time
import grpc

import Backtest.server.pb.backtest_pb2 as pb2
import Backtest.server.pb.backtest_pb2_grpc as pb2_grpc


def backtest(stub):
    code = '005669'
    print("发送：", code)
    response = stub.RunBacktest(pb2.RunBacktestReq(code=code))
    if response.result == True:
        print(f"回测 {response.code}，成功")
    else:
        print(f"回测 {response.code}，失败")


def backtest_stream(stub):

    codes = ["005669", "161127", "162411"]
    iterator = code_iter(codes)
    responses = stub.RunBacktestStream(iterator)
    for res in responses:
        if res.result == True:
            print(f"回测 {res.code}，成功")
        else:
            print(f"回测 {res.code}，失败")


def code_iter(codes):
    for c in codes:
        print("流式发送：", c)
        time.sleep(1)
        yield pb2.RunBacktestReq(code=c)


def run():
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = pb2_grpc.BacktestStub(channel)
        backtest(stub)
        backtest_stream(stub)


if __name__ == '__main__':
    run()