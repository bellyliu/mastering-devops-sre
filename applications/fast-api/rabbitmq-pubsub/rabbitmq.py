import aio_pika
import json
import asyncio
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractRobustConnection
from typing import Callable, Optional
from config import get_settings

settings = get_settings()


class RabbitMQManager:
    """Manager for RabbitMQ connections and operations"""
    
    def __init__(self):
        self.connection: Optional[AbstractRobustConnection] = None
        self.channel = None
    
    async def connect(self):
        """Establish connection to RabbitMQ"""
        self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        # Set QoS to process one message at a time
        await self.channel.set_qos(prefetch_count=1)
        print(f"Connected to RabbitMQ at {settings.RABBITMQ_URL}")
    
    async def disconnect(self):
        """Close RabbitMQ connection"""
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()
        print("Disconnected from RabbitMQ")
    
    async def declare_exchange(
        self,
        exchange_name: str,
        exchange_type: ExchangeType = ExchangeType.TOPIC,
        durable: bool = True
    ):
        """Declare an exchange"""
        exchange = await self.channel.declare_exchange(
            exchange_name,
            exchange_type,
            durable=durable
        )
        return exchange
    
    async def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
        exclusive: bool = False,
        auto_delete: bool = False
    ):
        """Declare a queue"""
        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete
        )
        return queue
    
    async def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str
    ):
        """Bind a queue to an exchange with a routing key"""
        queue = await self.declare_queue(queue_name)
        exchange = await self.declare_exchange(exchange_name)
        await queue.bind(exchange, routing_key=routing_key)
        print(f"Bound queue '{queue_name}' to exchange '{exchange_name}' with routing key '{routing_key}'")
        return queue
    
    async def publish_message(
        self,
        exchange_name: str,
        routing_key: str,
        message_body: dict,
        priority: int = 5,
        delivery_mode: DeliveryMode = DeliveryMode.PERSISTENT
    ):
        """Publish a message to an exchange"""
        exchange = await self.declare_exchange(exchange_name)
        
        message = Message(
            body=json.dumps(message_body).encode(),
            delivery_mode=delivery_mode,
            priority=priority,
            content_type="application/json"
        )
        
        await exchange.publish(
            message,
            routing_key=routing_key
        )
        
        print(f"Published message to exchange '{exchange_name}' with routing key '{routing_key}'")
        return True
    
    async def consume_messages(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False
    ):
        """Consume messages from a queue"""
        queue = await self.declare_queue(queue_name)
        
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(ignore_processed=auto_ack):
                    try:
                        body = json.loads(message.body.decode())
                        print(f"Received message from queue '{queue_name}': {body}")
                        await callback(body)
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        # Optionally: reject and requeue the message
                        # await message.reject(requeue=True)


# Global RabbitMQ manager instance
rabbitmq_manager = RabbitMQManager()


async def get_rabbitmq_manager():
    """Dependency to get RabbitMQ manager"""
    return rabbitmq_manager
