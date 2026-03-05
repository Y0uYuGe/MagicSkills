import asyncio
from datetime import datetime
from pathlib import Path
from magicskills.core.registry import ALL_SKILLS
from magicskills.core.skills import Skills

from llama_index.core.tools import FunctionTool
from llama_index.llms.deepseek import DeepSeek
# 详见 https://docs.llamaindex.org.cn/en/stable/api_reference/llms/
from llama_index.core.agent import ReActAgent


LLM_API_KEY = "LLM_API_KEY"
LLM_MODEL = "LLM_MODEL"
LLM_BASE_URL = "LLM_BASE_URL"

# 1. 加载技能
s1 = ALL_SKILLS.get_skill("pdf")
s2 = ALL_SKILLS.get_skill("explain-code")
paths = sorted({s.base_dir for s in [s1, s2]}, key=lambda p: p.as_posix())
my_skills = Skills(name="llamaindex-skills", skills=[s1, s2], paths=paths)

# 2. 创建LlamaIndex工具
def magic_skills_tool(action: str, arg: str = "") -> str:
    """MagicSkills unified tool interface"""
    result = my_skills.skill_for_all_agent(action, arg)
    return str(result)

skill_tool = FunctionTool.from_defaults(
    fn=magic_skills_tool,
    name="skill_tool",
    description=my_skills.tool_description
)

async def main():
    llm = DeepSeek(
        model=LLM_MODEL,
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL
    )
    # 创建ReAct Agent 并测试对话
    agent = ReActAgent(llm=llm, tools=[skill_tool])
    response = await agent.run("Please use the skill_tool tool to list all available skills.")
    print(response)
    log_file = Path(__file__).parent / "llamaindex_result.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(str(response))


if __name__ == "__main__":
    asyncio.run(main())