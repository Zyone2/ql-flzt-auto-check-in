#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLZT自动签到主逻辑模块
"""

import requests
import logging
from notification import BarkNotification
from config import (
    EMAIL, PASSWORD, LOGIN_URL, USER_INFO_URL,
    CHECK_IN_URL, CONVERT_TRAFFIC_URL,
    CONVERT_TRAFFIC, CONVERT_AMOUNT
)

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

def format_bytes(size):
    """智能格式化字节大小"""
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power and n < len(power_labels) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

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

            # 检查是否签到成功
            if result.get('data'):
                # 签到成功
                logger.info(f'[{self.account_info}] 签到成功: {result}')
                self.handle_success("签到成功")

            elif result.get('status') == 'fail' and 'already checked in' in str(result.get('message', '')).lower():
                # 已经签到过，视为成功
                logger.info(f'[{self.account_info}] 今日已签到过: {result.get("message")}')
                self.handle_success("今日已签到过")

            else:
                # 其他签到失败情况
                error_msg = f'[{self.account_info}] 签到失败: {result}'
                logger.error(error_msg)
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

    def handle_success(self, status):
        """处理签到成功后的逻辑"""
        # 获取用户信息
        try:
            r = self.s.get(url=USER_INFO_URL)
            data = r.json()

            if not data.get('data'):
                # 获取用户信息失败
                logger.warning(f'[{self.account_info}] 获取用户信息失败: {data}')
                self.send_success_notification(status, None)
                return

            user_data = data['data']

            # 获取签到奖励流量
            checkin_traffic = 0
            if user_data.get('checkin_reward_traffic'):
                checkin_traffic = int(user_data['checkin_reward_traffic'])
                logger.info(f'[{self.account_info}] 签到奖励流量: {format_bytes(checkin_traffic)}')

            # 构建用户信息字符串
            user_info = self.build_user_info(user_data, status, checkin_traffic)

            # 检查是否需要转换流量
            if CONVERT_TRAFFIC and checkin_traffic > 0:
                self.convert_traffic(checkin_traffic, user_info)
            else:
                # 不转换流量，直接发送通知
                self.send_success_notification(status, user_info)

        except Exception as e:
            logger.error(f'[{self.account_info}] 处理用户信息失败: {e}')
            # 发送简单通知
            notification = BarkNotification(
                title='FLZT签到完成',
                content=f'账号: {self.account_info}\n{status}\n获取用户信息失败'
            )
            notification.notify()

    def build_user_info(self, user_data, status, checkin_traffic):
        """构建用户信息字符串"""
        info_parts = []

        # 基本账号信息
        info_parts.append(f'账号: {self.account_info}')
        info_parts.append(f'状态: {status}')

        # 流量信息
        if user_data.get('transfer_enable'):
            transfer_enable = int(user_data['transfer_enable'])
            used = int(user_data.get('used', 0))
            remaining = transfer_enable - used

            info_parts.append(f'总流量: {format_bytes(transfer_enable)}')
            info_parts.append(f'已用流量: {format_bytes(used)}')
            info_parts.append(f'剩余流量: {format_bytes(remaining)}')

            if checkin_traffic > 0:
                info_parts.append(f'签到奖励: {format_bytes(checkin_traffic)}')

        return "\n".join(info_parts)

    def convert_traffic(self, checkin_traffic, user_info):
        """转换流量"""
        try:
            # 计算要转换的流量（字节）
            if CONVERT_AMOUNT > 0:
                # 转换指定流量（MB转换为字节）
                convert_amount_bytes = CONVERT_AMOUNT * 1024 * 1024
                # 不能超过签到奖励的流量
                convert_amount_bytes = min(convert_amount_bytes, checkin_traffic)
                convert_desc = f'{CONVERT_AMOUNT}MB'
            else:
                # 转换全部流量
                convert_amount_bytes = checkin_traffic
                convert_desc = '全部'

            # 转换为MB（接口可能需要MB单位）
            convert_amount_mb = convert_amount_bytes // (1024 * 1024)

            if convert_amount_mb <= 0:
                logger.info(f'[{self.account_info}] 转换流量过少，跳过转换')
                notification = BarkNotification(
                    title='FLZT签到完成',
                    content=f'{user_info}\n转换流量: 流量过少，未转换'
                )
                notification.notify()
                return

            # 发送转换请求
            r = self.s.post(url=CONVERT_TRAFFIC_URL, data={'transfer': convert_amount_mb})
            result = r.json()

            if result.get('data'):
                logger.info(f'[{self.account_info}] 转换流量成功: {result}')
                notification = BarkNotification(
                    title='FLZT签到完成 ✅',
                    content=f'{user_info}\n转换流量: {convert_desc} ({format_bytes(convert_amount_bytes)}) 成功'
                )
                notification.notify()
            else:
                error_msg = f'[{self.account_info}] 转换流量可能失败: {result}'
                logger.warning(error_msg)
                notification = BarkNotification(
                    title='FLZT签到完成 ⚠️',
                    content=f'{user_info}\n转换流量: {convert_desc} 失败\n错误信息: {result}'
                )
                notification.notify()

        except Exception as e:
            logger.error(f'[{self.account_info}] 转换流量失败: {e}')
            notification = BarkNotification(
                title='FLZT签到完成 ⚠️',
                content=f'{user_info}\n转换流量: 失败\n错误信息: {e}'
            )
            notification.notify()

    def send_success_notification(self, status, user_info):
        """发送成功通知（不转换流量时使用）"""
        if user_info:
            content = user_info
        else:
            content = f'账号: {self.account_info}\n{status}'

        notification = BarkNotification(
            title='FLZT签到完成 ✅',
            content=content
        )
        notification.notify()