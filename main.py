#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FLZT自动签到脚本 - 青龙面板版本
使用方法:
1. 在青龙面板环境变量中设置:
   - FLZT_BASE_URL: 站点基础URL
   - FLZT_EMAIL: 登录邮箱
   - FLZT_PASSWORD: 登录密码
2. 设置定时任务: 0 9 * * *
"""

import logging
import sys
from flzt import FLZT

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def main():
    """主函数 - 青龙面板将执行此函数"""
    try:
        logger = logging.getLogger(__name__)
        logger.info('=' * 50)
        logger.info('FLZT自动签到任务开始')
        logger.info('=' * 50)

        # 创建并执行任务
        flzt = FLZT()
        flzt.run()

        logger.info('=' * 50)
        logger.info('FLZT自动签到任务结束')
        logger.info('=' * 50)

    except Exception as e:
        logging.error(f'任务执行失败: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()