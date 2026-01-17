import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
from astrbot.core.message.message_event_result import ResultContentType


@register("clean_response", "Amnemon", "清除括号内AI的心声还有动作神态描写及/符号", "1.0.1")
class CleanResponse(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        logger.info("[CleanResponse] 插件已初始化！")

    @filter.on_decorating_result()
    async def on_decorating_result(self, event: AstrMessageEvent, *args):
        logger.info("[CleanResponse] >>> HOOK 被触发！开始处理 <<<")
        
        result = event.get_result()
        if not result:
            logger.warning("[CleanResponse] result 为 None")
            return
        if not hasattr(result, 'chain'):
            logger.warning("[CleanResponse] result 无 chain 属性")
            return
        if not result.chain:
            logger.warning("[CleanResponse] chain 为空")
            return

        logger.info(f"[CleanResponse] 原始 chain: {[str(c) for c in result.chain]}")

        # 提取文本
        full_text = ""
        plain_indices = []
        for i, comp in enumerate(result.chain):
            if isinstance(comp, Comp.Plain):
                full_text += comp.text + " "
                plain_indices.append(i)
        full_text = full_text.strip()

        logger.info(f"[CleanResponse] 提取到文本: '{full_text}'")

        if not full_text:
            logger.info("[CleanResponse] 无有效文本，跳过")
            return

        # 修正正则 + 增加清除 / 符号的逻辑
        # 1. 匹配并删除中英文括号及内部内容  2. 匹配并删除 / 符号
        cleaned = re.sub(r'（[^）]*）|\([^)]*\)|/', '', full_text).strip()

        # 替换 Plain
        for idx in sorted(plain_indices, reverse=True):
            del result.chain[idx]
        if plain_indices:
            result.chain.insert(plain_indices[0], Comp.Plain(cleaned))

        logger.info(f"[CleanResponse] 处理完成！新文本: '{cleaned}'")
