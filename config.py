#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境变量配置模块 - 为避免与系统env冲突改名为config
从青龙面板环境变量读取配置
"""

import os

# 从青龙面板环境变量读取
BASE_URL = os.environ.get('FLZT_BASE_URL', '').strip()
if not BASE_URL:
    raise ValueError("请在青龙面板环境变量中设置 FLZT_BASE_URL")

EMAIL = os.environ.get('FLZT_EMAIL', '').strip()
PASSWORD = os.environ.get('FLZT_PASSWORD', '').strip()

# API URLs
LOGIN_URL = BASE_URL + '/api/v1/passport/auth/login'
CHECK_IN_URL = BASE_URL + '/api/v1/user/checkIn'
USER_INFO_URL = BASE_URL + '/api/v1/user/info'
CONVERT_TRAFFIC_URL = BASE_URL + '/api/v1/user/checkIn'

# 账号检查
if not EMAIL or not PASSWORD:
    raise ValueError("请在青龙面板环境变量中设置 FLZT_EMAIL 和 FLZT_PASSWORD")

print(f"[配置加载] BASE_URL: {BASE_URL}")
print(f"[配置加载] EMAIL: {EMAIL[:3]}***{EMAIL.split('@')[1] if '@' in EMAIL else ''}")