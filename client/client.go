package main

import (
	info "client/pb"
	"context"
	"fmt"
	"sync"

	"google.golang.org/grpc"
)

func backtest(client info.BacktestClient) {
	code := "005669"
	fmt.Println("发送：", code)
	res, err := client.RunBacktest(context.Background(), &info.RunBacktestReq{Code: code})
	if err != nil {
		fmt.Println(err)
	}
	if res.Result {
		fmt.Printf("回测 %v ，成功\n", res.Code)
	} else {
		fmt.Printf("回测 %v ，失败\n", res.Code)
	}
}

func backtestStream(client info.BacktestClient) {

	codes := []string{"005669", "161127", "162411"}

	c, _ := client.RunBacktestStream(context.Background())
	wg := sync.WaitGroup{}
	wg.Add(len(codes))
	go func() {
		for _, code := range codes {
			fmt.Println("流式发送：", code)
			err := c.Send(&info.RunBacktestReq{Code: code})
			if err != nil {
				fmt.Println(err)
				wg.Done()
				break
			}
		}
	}()

	go func() {
		for {
			res, err := c.Recv()
			if err != nil {
				fmt.Println(err)
				wg.Done()
				break
			}
			if res.Result {
				fmt.Printf("回测 %v ，成功\n", res.Code)
				wg.Done()
			} else {
				fmt.Printf("回测 %v ，失败\n", res.Code)
				wg.Done()
			}
		}
	}()

	wg.Wait()
	fmt.Println("流式回测结束")

}

func main() {
	l, _ := grpc.Dial("127.0.0.1:50052", grpc.WithInsecure())
	client := info.NewBacktestClient(l)

	backtest(client)
	backtestStream(client)

}
