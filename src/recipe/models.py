from __future__ import annotations

from pydantic import BaseModel


class Ingredient(BaseModel):
    name: str
    amount: str
    required: bool


class NutritionTable(BaseModel):
    calories_kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float
    fiber_g: float
    sodium_mg: float
    score: str  # A-F


class Recipe(BaseModel):
    title: str
    servings_note: str
    ingredients: list[Ingredient]
    steps: list[str]
    nutrition: NutritionTable | None = None


SYSTEM_PROMPT = """\
你是一位专业的食谱整理助手。用户会提供一段烹饪视频的文字转录内容，请你根据转录内容整理出一份结构化的食谱。

要求：
1. 食谱标题应简洁明了
2. 将所有食材份量调整为1人份
3. servings_note 字段填写"1人份"
4. ingredients 中每个食材标注 name（名称）、amount（用量，含单位）、required（是否必需）
5. steps 为烹饪步骤列表，每步简洁清晰，有可操作行，要包含必要的细节，例如温度，火候，时长和操作要点等
6. nutrition 为估算的营养成分，包括热量，钠，蛋白质，脂肪，碳水化合物，膳食纤维等，并给出一个A-F的营养评分（A最好，F最差）
7. 输出格式必须严格遵守以下JSON结构，且只能输出JSON，不要添加任何解释或文本：

请严格以如下 JSON 格式输出，不要输出任何其他内容：
{
  "title": "菜名",
  "servings_note": "1人份",
  "ingredients": [
    {"name": "食材名", "amount": "用量", "required": true}
  ],
  "steps": ["步骤1", "步骤2"],
  "nutrition": {
    "calories_kcal": 0,
    "protein_g": 0,
    "fat_g": 0,
    "carbs_g": 0,
    "fiber_g": 0,
    "sodium_mg": 0,
    "score": "A"
  }
}
"""


def recipe_to_markdown(recipe: Recipe) -> str:
    lines = [f"# {recipe.title}", "", f"*{recipe.servings_note}*", ""]

    lines.append("## 食材")
    lines.append("")
    lines.append("| 食材 | 用量 | 必需 |")
    lines.append("|------|------|------|")
    for ing in recipe.ingredients:
        req = "是" if ing.required else "否"
        lines.append(f"| {ing.name} | {ing.amount} | {req} |")
    lines.append("")

    lines.append("## 步骤")
    lines.append("")
    for i, step in enumerate(recipe.steps, 1):
        lines.append(f"{i}. {step}")
    lines.append("")

    if recipe.nutrition:
        try:
            n = recipe.nutrition
            lines.append("## 营养成分（估算）")
            lines.append("")
            lines.append(f"- 热量: {n.calories_kcal} kcal")
            lines.append(f"- 蛋白质: {n.protein_g} g")
            lines.append(f"- 脂肪: {n.fat_g} g")
            lines.append(f"- 碳水化合物: {n.carbs_g} g")
            lines.append(f"- 膳食纤维: {n.fiber_g} g")
            lines.append(f"- 钠: {n.sodium_mg} mg")
            lines.append(f"- 营养评分: {n.score}")
            lines.append("")
        except Exception:
            pass

    return "\n".join(lines)
