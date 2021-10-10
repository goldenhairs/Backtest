# Backtest
基金回测服务

生成 golang pb 文件:

```shell
cd ./server/pb/
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative backtest.proto
```