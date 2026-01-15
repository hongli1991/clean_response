import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import astrbot.api.message_components as Comp
from astrbot.core.message.message_event_result import ResultContentType


@register("clean_response", "Amnemon", "清除括号内AI的心声还有动作神态描写", "1.0.0")
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

        # 暂时跳过 LLM 判断（调试用）
        # try:
        #     is_llm = result.is_llm_result()
        # except:
        #     is_llm = getattr(result, "result_content_type", None) == ResultContentType.LLM_RESULT
        # if not is_llm:
        #     logger.info("[CleanResponse] 非 LLM 响应")
        #     return

        # 简单清洗：只去括号
        cleaned = re.sub(r'（[^）]*）/s|\([^)]*\)', '', full_text).strip()

        # 替换 Plain
        for idx in sorted(plain_indices, reverse=True):
            del result.chain[idx]
        if plain_indices:
            result.chain.insert(plain_indices[0], Comp.Plain(cleaned))


        logger.info(f"[CleanResponse] 处理完成！新文本: '{cleaned}'")
