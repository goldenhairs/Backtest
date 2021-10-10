from concurrent import futures
import grpc
import Backtest.server.pb.backtest_pb2 as pb2
import Backtest.server.pb.backtest_pb2_grpc as pb2_grpc

from Backtest.server.backtest import upload_backtest_data
from Backtest.server.util.config import Config
from Backtest.server.util.log import get_logger

logger = get_logger(__file__)
config = Config()


class Backtest(pb2_grpc.BacktestServicer):

    def RunBacktest(self, request, context):
        res = upload_backtest_data(request.code)
        return pb2.RunBacktestRes(code=request.code, result=res)

    def RunBacktestStream(self, request_iterator, context):
        for req in request_iterator:
            res = upload_backtest_data(req.code)
            yield pb2.RunBacktestRes(code=req.code, result=res)


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_BacktestServicer_to_server(Backtest(), server)

    server.add_insecure_port(f"[::]:{config.server_port}")
    server.start()

    logger.info(f"Backtest server started, port: {config.server_port}")
    server.wait_for_termination()


if __name__ == '__main__':

    serve()
