#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLZT自动签到主逻辑模块
"""

import requests
import logging
from notification import BarkNotification
from config import EMAIL, PASSWORD, LOGIN_URL, USER_INFO_URL, CHECK_IN_URL

logger = logging.getLogger(__name__)

def format_traffic(traffic, s='MB'):
    """流量格式化"""
    if s == 'KB':
        return str(round(traffic / 1024, 2)) + 'KB'
    elif s == 'MB':
        return str(round(traffic / 1024 / 1024, 2)) + 'MB'
    elif s == 'GB':
        return str(round(traffic / 1024 / 1024 / 1024, 2)) + 'GB'
    else:
        return str(traffic)

class FLZT:
    def __init__(self, email=None, password=None):
        self.email = email if email else EMAIL
        self.password = password if password else PASSWORD
        self.s = requests.Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0'
        })
        # 账号信息脱敏处理
        if '@' in self.email:
            prefix = self.email.split('@')[0]
            if len(prefix) > 5:
                masked_email = f"{prefix[:2]}***{prefix[-2:]}@{self.email.split('@')[1]}"
            else:
                masked_email = f"{prefix[:1]}***@{self.email.split('@')[1]}"
            self.account_info = masked_email
        else:
            self.account_info = f"{self.email[:3]}***"

    def run(self):
        """主执行流程"""
        logger.info(f'开始执行账号: {self.account_info}')

        # 登录
        try:
            r = self.s.post(url=LOGIN_URL, data={
                'email': self.email, 'password': self.password})
            data = r.json()
            if data.get('data') and data['data'].get('auth_data'):
                token = data['data']['auth_data']
                self.s.headers.update({'Authorization': token})
                logger.info(f'[{self.account_info}] 登录成功')
            else:
                error_msg = f'[{self.account_info}] 登录失败: {data}'
                logger.error(error_msg)
                # 登录失败时发送通知
                notification = BarkNotification(
                    title='FLZT登录失败',
                    content=f'账号: {self.account_info}\n错误信息: {data}'
                )
                notification.notify()
                return
        except Exception as e:
            error_msg = f'[{self.account_info}] 登录失败: {e}'
            logger.error(error_msg)
            # 登录失败时发送通知
            notification = BarkNotification(
                title='FLZT登录失败',
                content=f'账号: {self.account_info}\n错误信息: {e}'
            )
            notification.notify()
            return

        # 签到
        try:
            r = self.s.get(url=CHECK_IN_URL)
            result = r.json()
            if result.get('data'):
                logger.info(f'[{self.account_info}] 签到成功: {result}')

                # 获取用户信息以显示当前状态
                try:
                    r = self.s.get(url=USER_INFO_URL)
                    data = r.json()
                    if data.get('data'):
                        # 发送签到成功通知
                        notification = BarkNotification(
                            title='FLZT签到成功 🎉',
                            content=f'账号: {self.account_info}\n签到成功\n状态: ✅ 完成'
                        )
                        notification.notify()
                    else:
                        # 获取用户信息失败，但仍发送签到成功通知
                        notification = BarkNotification(
                            title='FLZT签到成功 🎉',
                            content=f'账号: {self.account_info}\n签到完成\n状态: ✅ 成功'
                        )
                        notification.notify()
                except Exception as e:
                    logger.warning(f'[{self.account_info}] 获取用户信息失败，但签到已完成: {e}')
                    # 发送签到成功通知
                    notification = BarkNotification(
                        title='FLZT签到成功 🎉',
                        content=f'账号: {self.account_info}\n签到完成\n状态: ✅ 成功'
                    )
                    notification.notify()
            else:
                error_msg = f'[{self.account_info}] 签到失败: {result}'
                logger.error(error_msg)
                # 签到失败时发送通知
                notification = BarkNotification(
                    title='FLZT签到失败',
                    content=f'账号: {self.account_info}\n错误信息: {result}\n状态: ❌ 失败'
                )
                notification.notify()
        except Exception as e:
            error_msg = f'[{self.account_info}] 签到失败: {e}'
            logger.error(error_msg)
            # 签到失败时发送通知
            notification = BarkNotification(
                title='FLZT签到失败',
                content=f'账号: {self.account_info}\n错误信息: {e}\n状态: ❌ 失败'
            )
            notification.notify()

        logger.info(f'账号 {self.account_info} 执行完成')