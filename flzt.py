#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLZT自动签到主逻辑模块
"""

import requests
import logging
from notification import BarkNotification
from config import EMAIL, PASSWORD, LOGIN_URL, USER_INFO_URL, CONVERT_TRAFFIC_URL, CHECK_IN_URL

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
            else:
                logger.warning(f'[{self.account_info}] 签到可能失败: {result}')
        except Exception as e:
            logger.error(f'[{self.account_info}] 签到失败: {e}')
            return

        traffic = 0
        # 获取用户信息
        try:
            r = self.s.get(url=USER_INFO_URL)
            data = r.json()
            if data.get('data') and data['data'].get('checkin_reward_traffic'):
                traffic = int(data['data']['checkin_reward_traffic'])
                logger.info(f'[{self.account_info}] 获取用户信息成功，剩余签到流量: {format_traffic(traffic)}')
            else:
                logger.warning(f'[{self.account_info}] 未获取到流量信息: {data}')
                return
        except Exception as e:
            logger.error(f'[{self.account_info}] 获取用户信息失败: {e}')
            return

        # 转换流量
        if traffic > 0:
            try:
                r = self.s.post(url=CONVERT_TRAFFIC_URL, data={'transfer': traffic})
                result = r.json()
                if result.get('data'):
                    logger.info(f'[{self.account_info}] 转换流量成功: {result}')

                    # 发送成功通知
                    notification = BarkNotification(
                        title='FLZT签到成功 🎉',
                        content=f'账号: {self.account_info}\n签到流量转换成功\n已转换流量: {format_traffic(traffic)}\n状态: ✅ 成功'
                    )
                    notification.notify()
                else:
                    error_msg = f'[{self.account_info}] 转换流量可能失败: {result}'
                    logger.warning(error_msg)
                    # 转换失败时发送通知
                    notification = BarkNotification(
                        title='FLZT流量转换警告',
                        content=f'账号: {self.account_info}\n转换流量可能失败\n状态: ⚠️ 警告'
                    )
                    notification.notify()
            except Exception as e:
                error_msg = f'[{self.account_info}] 转换流量失败: {e}'
                logger.error(error_msg)
                # 转换失败时发送通知
                notification = BarkNotification(
                    title='FLZT流量转换失败',
                    content=f'账号: {self.account_info}\n转换流量失败\n状态: ❌ 失败'
                )
                notification.notify()
        else:
            logger.info(f'[{self.account_info}] 没有可转换的流量')

            # 没有流量时发送通知
            notification = BarkNotification(
                title='FLZT签到完成',
                content=f'账号: {self.account_info}\n今日已签到\n没有可转换的流量\n状态: ⓘ 完成'
            )
            notification.notify()

        logger.info(f'账号 {self.account_info} 执行完成')