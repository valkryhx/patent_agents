#!/usr/bin/env python3
"""
测试队列操作是否正常
"""

import asyncio
import time

async def test_queue():
    """测试队列的基本操作"""
    print("🔍 测试队列操作...")
    
    # 创建一个队列
    queue = asyncio.Queue()
    print(f"✅ 队列创建成功，ID: {id(queue)}")
    
    # 检查初始状态
    print(f"📊 初始队列大小: {queue.qsize()}")
    
    # 放入一个消息
    test_message = {"type": "test", "content": "Hello World"}
    await queue.put(test_message)
    print(f"📤 消息已放入队列")
    print(f"📊 放入后队列大小: {queue.qsize()}")
    
    # 等待一小段时间
    await asyncio.sleep(0.1)
    print(f"📊 等待后队列大小: {queue.qsize()}")
    
    # 获取消息
    try:
        message = await asyncio.wait_for(queue.get(), timeout=1.0)
        print(f"📥 消息已获取: {message}")
        print(f"📊 获取后队列大小: {queue.qsize()}")
    except asyncio.TimeoutError:
        print("❌ 获取消息超时")
    
    print("✅ 队列测试完成")

async def test_concurrent_queue():
    """测试并发队列操作"""
    print("\n🔍 测试并发队列操作...")
    
    queue = asyncio.Queue()
    print(f"✅ 队列创建成功，ID: {id(queue)}")
    
    # 生产者任务
    async def producer():
        for i in range(3):
            message = {"id": i, "content": f"Message {i}"}
            await queue.put(message)
            print(f"📤 生产者放入消息 {i}")
            await asyncio.sleep(0.1)
    
    # 消费者任务
    async def consumer():
        for i in range(3):
            try:
                message = await asyncio.wait_for(queue.get(), timeout=2.0)
                print(f"📥 消费者获取消息: {message}")
                await asyncio.sleep(0.1)
            except asyncio.TimeoutError:
                print(f"❌ 消费者 {i} 获取消息超时")
    
    # 并发执行
    await asyncio.gather(producer(), consumer())
    print(f"📊 最终队列大小: {queue.qsize()}")
    print("✅ 并发队列测试完成")

async def main():
    """主测试函数"""
    print("🚀 开始队列测试...")
    print("=" * 50)
    
    await test_queue()
    await test_concurrent_queue()
    
    print("\n" + "=" * 50)
    print("🎉 所有测试完成！")

if __name__ == "__main__":
    asyncio.run(main())