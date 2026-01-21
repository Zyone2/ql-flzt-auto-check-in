#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bark推送模块 - 青龙面板专用版本
青龙面板内置了通知推送功能，我们直接调用即可
"""

import logging
import os

logger = logging.getLogger(__name__)

class Notification:
    def notify(self):
        pass

class BarkNotification(Notification):
    def __init__(self, title, content):
        super().__init__()
        self.title = title
        self.content = content

    def notify(self):
        """使用青龙面板的推送功能发送Bark通知"""
        try:
            # 青龙面板提供了 send 函数用于推送
            # 这里模拟调用青龙的推送机制
            # 实际运行时，青龙会自动处理推送
            
            # 构造推送消息
            message = f"{self.title}\n\n{self.content}"
            
            # 在青龙面板中，推送通常通过环境变量配置
            # 我们只需打印出推送内容，青龙会自动捕获并推送
            print(f"【Bark推送】{self.title}")
            print(f"{self.content}")
            
            logger.info(f'Bark通知准备发送: {self.title}')
            
            # 尝试使用青龙内置的推送（如果可用）
            try:
                # 青龙面板通常有 ql.send 或其他推送方式
                # 这里尝试多种可能的推送方法
                self._try_qinglong_push()
            except Exception as e:
                logger.debug(f'使用青龙内置推送失败，使用标准输出: {e}')
                
        except Exception as e:
            logger.error(f'发送通知时出错: {e}')

    def _try_qinglong_push(self):
        """尝试调用青龙面板的内置推送函数"""
        # 方法1: 尝试导入青龙的推送模块
        try:
            import sys
            sys.path.append('/ql/scripts')
            from notify import send as ql_send
            ql_send(self.title, self.content)
            logger.info('已使用青龙推送模块发送通知')
            return True
        except ImportError:
            pass
        
        # 方法2: 尝试使用环境变量中的推送配置
        bark_key = os.environ.get('BARK_PUSH')
        if bark_key:
            # 如果有BARK_PUSH环境变量，可以自行构造推送
            import requests
            import urllib.parse
            
            # 对标题和内容进行URL编码
            encoded_title = urllib.parse.quote(self.title)
            encoded_content = urllib.parse.quote(self.content)
            
            # 构造Bark推送URL
            url = f"https://api.day.app/{bark_key}/{encoded_title}/{encoded_content}"
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info('Bark推送发送成功')
                else:
                    logger.warning(f'Bark推送发送失败: {response.text}')
            except Exception as e:
                logger.error(f'Bark推送请求失败: {e}')
            return True
            
        return False