#!/usr/bin/env python3
"""
市场研究报告视觉生成器

使用
scientific-schematics和generate-image技能批量
生成市场研究报告的视觉内容。

默认行为：仅生成5-6个核心视觉内容
使用--all标志生成所有28个扩展视觉内容

用法：
    # 生成核心5-6个视觉内容（推荐开始报告时使用）
    python generate_market_visuals.py --topic "电动汽车充电" --output-dir figures/

    # 生成所有28个视觉内容（用于综合覆盖）
    python generate_market_visuals.py --topic "AI医疗健康" --output-dir figures/ --all

    # 跳过现有文件
    python generate_market_visuals.py --topic "主题" --output-dir figures/ --skip-existing
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


# 包含提示的视觉定义
# 每个元组：(文件名, 工具, 提示模板, is_core)
# is_core=True为最初生成的5-6个基本视觉内容

CORE_VISUALS = [
    # 优先级1：市场增长轨迹
    (
        "01_market_growth_trajectory.png",
        "scientific-schematics",
        "条形图{主题}市场增长2020年至2034年。历史条形2020-2024年深蓝色，"
        "预测条形2025-2034年浅蓝色。Y轴十亿美元，X轴年份。"
        "CAGR注释。每个条形上数据标签。2024和2025年之间垂直虚线。标题：市场增长轨迹。专业白色背景",
    ),
    # 优先级2：TAM/SAM/SOM
    (
        "02_tam_sam_som.png",
        "scientific-schematics",
        "{主题}市场TAM SAM SOM同心圆。外圆TAM总可获得"
        "市场。中圆SAM可服务可获得市场。内圆SOM可获得"
        "服务市场。每个都标记首字母缩写、全称。"
        "蓝色渐变最外层到最内层浅色。白色背景专业外观",
    ),
    # 优先级3：波特五力
    (
        "03_porters_five_forces.png",
        "scientific-schematics",
        "{主题}波特五力图。中心框竞争对抗带评级。"
        "四个围绕框带箭头到中心：顶部新进入者威胁，"
        "左侧供应商议价能力，右侧买方议价能力，"
        "底部替代品威胁。颜色编码高红、中黄、低绿。"
        "每个框包含2-3个关键因素。专业外观",
    ),
    # 优先级4：竞争定位矩阵
    (
        "04_competitive_positioning.png",
        "scientific-schematics",
        "2x2竞争定位矩阵{主题}。X轴市场焦点细分到广泛。"
        "Y轴解决方案方法产品到平台。象限：右上平台领导者，"
        "左上细分平台，右下产品领导者，左下专家。"
        "绘制8-10个带名称的公司圆圈。圆圈大小=市场份额。"
        "大小的图例。专业外观",
    ),
    # 优先级5：风险热图
    (
        "05_risk_heatmap.png",
        "scientific-schematics",
        "风险热图矩阵{主题}。X轴影响低中高关键。"
        "Y轴概率不太可能可能很可能很可能。"
        "单元格颜色：绿色低风险，黄色中等，橙色高风险，红色关键风险。"
        "绘制10-12个编号风险R1 R2等作为标签点。"
        "风险名称图例。专业清晰",
    ),
    # 优先级6：执行摘要信息图（可选）
    (
        "06_exec_summary_infographic.png",
        "generate-image",
        "{主题}市场研究的执行摘要信息图，单页布局，"
        "中央大指标显示市场规模，四个象限显示增长率"
        "关键参与者主要细分区域领导者，现代扁平设计，专业"
        "蓝绿配色方案，干净白色背景，企业商务美学",
    ),
]

EXTENDED_VISUALS = [
    # 行业生态系统
    (
        "07_industry_ecosystem.png",
        "scientific-schematics",
        "{主题}市场的行业生态系统价值链图。水平流程左"
        "到右：供应商框→制造商框→分销商框→最终用户框。"
        "每个主框下面显示3-4个更小的示例参与者类型框。产品流程实心箭头，"
        "资金流程虚线箭头。监管监督层在上面。"
        "专业蓝配色方案，白色背景，清晰标签",
    ),
    # 区域分解
    (
        "08_regional_breakdown.png",
        "scientific-schematics",
        "{主题}饼图区域市场分解。北美40%深蓝，"
        "欧洲28%中蓝，亚太22%绿，拉丁美6%浅蓝，"
        "中东非洲4%灰蓝。显示每片百分"
        "比。右侧图例。标题：按区域的市场规模。专业外观",
    ),
    # 细分增长
    (
        "09_segment_growth.png",
        "scientific-schematics",
        "水平条形图{主题}细分增长比较。Y轴5-6个细分名称，"
        "X轴CAGR百分比0-30%。条形颜色从最高绿到最低蓝。"
        "带百分比的数据标签。从最高到最低排序。"
        "标题：细分增长率比较。包含市场平均线",
    ),
    # 驱动因素影响矩阵
    (
        "10_driver_impact_matrix.png",
        "scientific-schematics",
        "2x2矩阵{主题}驱动因素影响评估。X轴影响低到高，"
        "Y轴概率低到高。象限：右上关键驱动者红，"
        "左上监控黄，右下仔细观察黄，"
        "左下较低优先级绿。绘制8个标签驱动者圆圈在位置。"
        "圆圈大小表示当前影响。专业清晰标签",
    ),
    # PESTLE分析
    (
        "11_pestle_analysis.png",
        "scientific-schematics",
        "{主题}市场的PESTLE六边形图。中心六边形标记市场分析。"
        "六个围绕六边形：政治红、经济蓝、社会绿、"
        "技术橙、法律紫、环境绿。每个外六边形"
        "有2-3个关键因素的要点。连接中心到每个的线。"
        "专业外观清晰可读文本",
    ),
    # 趋势时间线
    (
        "12_trends_timeline.png",
        "scientific-schematics",
        "水平时间线{主题}趋势2024到2030年。在不同年份"
        "绘制6-8个新兴趋势。每个趋势带图标、名称、简要描述。颜色编码："
        "技术趋势蓝、市场趋势绿、监管趋势橙。"
        "2024年当前标记。专业清晰标签",
    ),
    # 市场份额图
    (
        "13_market_share.png",
        "scientific-schematics",
        "饼图市场份额{主题}前10家公司。公司A18%深蓝，"
        "公司B15%中蓝，公司C12%绿，公司D10%浅蓝，"
        "5家更多公司5-8%各种蓝，其他15%灰。"
        "切片上的百分比标签。带公司名称的图例。"
        "标题：按公司的市场份额。色盲友好颜色专业",
    ),
    # 战略群体图
    (
        "14_strategic_groups.png",
        "scientific-schematics",
        "战略群体图{主题}。X轴地理范围区域到全球。"
        "Y轴产品宽度窄到宽。绘制4-5个战略群体的椭圆气泡。"
        "每个气泡包含2-4个公司名称。气泡大小=集体市场份额。"
        "标记群体：全球综合者、区域专家、专注创新者。"
        "每个群体不同颜色。专业清晰标签",
    ),
    # 客户细分
    (
        "15_customer_segments.png",
        "scientific-schematics",
        "树图客户细分{主题}。大企业45%深蓝，"
        "中市场30%中蓝，中小型企业18%浅蓝，消费者7%绿。"
        "每个细分显示名称和百分比。标题：按市场份额的客户细分。"
        "专业外观清晰标签",
    ),
    (
        "16_segment_attractiveness.png",
        "scientific-schematics",
        "2x2细分吸引力矩阵{主题}。X轴细分规模小到大。"
        "Y轴增长率低到高。象限：右上优先大量投资绿，"
        "左上投资增长黄，右下收获橙，"
        "左下去优先级灰。将客户细分绘制为圆圈。"
        "圆圈大小=盈利能力。不同颜色。专业",
    ),
    (
        "17_customer_journey.png",
        "scientific-schematics",
        "客户旅程水平流程图{主题}。5个阶段从左到右：认知，"
        "考虑、决策、实施、倡导。每个阶段在下方行中显示关键活动、"
        "痛点、接触点。每个阶段图标。"
        "从浅到深颜色渐变。专业清晰标签",
    ),
    # 技术路线图
    (
        "18_technology_roadmap.png",
        "scientific-schematics",
        "技术路线图{主题}2024年到2030年。三条平行水平轨道："
        "核心技术蓝，新兴技术绿，使能技术橙。"
        "每个轨道标记里程碑和技术引入标记。垂直线连接相关技术。"
        "年份标记。技术名称标记。专业外观",
    ),
    (
        "19_innovation_curve.png",
        "scientific-schematics",
        "{主题}技术的Gartner炒作周期曲线。五个阶段：创新触发"
        "上升，膨胀期望峰值在顶部，幻灭低谷在底部，"
        "启蒙斜坡上升，生产力高原稳定。"
        "在曲线上绘制6-8个技术带标签。按类别着色。专业清晰标签",
    ),
    # 监管时间线
    (
        "20_regulatory_timeline.png",
        "scientific-schematics",
        "监管时间线{主题}2020年到2028年。过去法规深蓝实心标记，"
        "当前绿标记，即将到来浅蓝虚线。每个显示法规名称、日期、"
        "简要描述。2024年NOW垂直线。专业外观清晰标签",
    ),
    # 风险缓解矩阵
    (
        "21_risk_mitigation.png",
        "scientific-schematics",
        "风险缓解图{主题}。左列风险橙红框。"
        "右列缓解策略绿蓝框。"
        "箭头连接风险到缓解。按类别分组。风险严重程度按颜色强度。"
        "包含预防和响应。专业清晰标签",
    ),
    # 机会矩阵
    (
        "22_opportunity_matrix.png",
        "scientific-schematics",
        "2x2机会矩阵{主题}。X轴市场吸引力低到高。"
        "Y轴获胜能力低到高。象限：右上积极追求绿，"
        "左上建设能力黄，右下选择性投资黄，"
        "左下避免红。绘制6-8个带标签的机会圆圈。"
        "大小=机会价值。专业",
    ),
    # 建议优先级矩阵
    (
        "23_recommendation_priority.png",
        "scientific-schematics",
        "2x2{主题}建议优先级矩阵。X轴努力低到高。"
        "Y轴影响低到高。象限：左上快速赢绿先做，"
        "右上重大项目蓝仔细计划，左上填充物灰有时间做，"
        "右下吃力不讨好的任务红避免。绘制6-8个编号建议。专业",
    ),
    # 实施时间线
    (
        "24_implementation_timeline.png",
        "scientific-schematics",
        "甘特图{主题}实施24个月。阶段1基础1-6月深蓝。"
        "阶段2建设4-12月中蓝。阶段3扩展10-18月绿。"
        "阶段4优化16-24月浅蓝。重叠条。"
        "关键里程碑为钻石。月标记X轴。专业",
    ),
    # 里程碑跟踪器
    (
        "25_milestone_tracker.png",
        "scientific-schematics",
        "里程碑跟踪器{主题}水平时间线8-10个里程碑。"
        "每个显示日期、名称、状态：完成绿检查，进行中黄圆圈，"
        "即将到来灰圆圈。按阶段分组。阶段标签上方。"
        "连接时间线线。专业",
    ),
    # 财务预测
    (
        "26_financial_projections.png",
        "scientific-schematics",
        "组合条形和折线图{主题}5年预测。条形图收入"
        "主Y轴美元。折线图增长率次Y轴百分比。"
        "三种情景：保守灰，基础情况蓝，乐观绿。"
        "X轴第1-5年。数据标签。图例。标题财务预测5年。专业",
    ),
    # 情景分析
    (
        "27_scenario_analysis.png",
        "scientific-schematics",
        "分组条形图{主题}情景比较。X轴指标：收入Y5，"
        "EBITDA Y5，市场份额，ROI。每组三个条形：保守灰，"
        "基础情况蓝，乐观绿。数据标签。图例。"
        "标题情景分析比较。专业清晰标签",
    ),
]


def get_script_path(tool: str) -> Path:
    """获取适当生成脚本的路径。"""
    base_path = Path(__file__).parent.parent.parent  # 技能目录

    if tool == "scientific-schematics":
        return base_path / "scientific-schematics" / "scripts" / "generate_schematic.py"
    elif tool == "generate-image":
        return base_path / "generate-image" / "scripts" / "generate_image.py"
    else:
        raise ValueError(f"未知工具: {tool}")


def generate_visual(
    filename: str,
    tool: str,
    prompt: str,
    output_dir: Path,
    topic: str,
    skip_existing: bool = False,
    verbose: bool = False,
) -> bool:
    """使用适当工具生成单个视觉内容。"""
    output_path = output_dir / filename

    # 如果存在且skip_existing为True则跳过
    if skip_existing and output_path.exists():
        if verbose:
            print(f"  [跳过] {filename} 已存在")
        return True

    # 用主题格式化提示
    formatted_prompt = prompt.format(topic=topic)

    # 获取脚本路径
    script_path = get_script_path(tool)

    if not script_path.exists():
        print(f"  [错误] 未找到脚本: {script_path}")
        return False

    # 构建命令
    if tool == "scientific-schematics":
        cmd = [
            sys.executable,
            str(script_path),
            formatted_prompt,
            "-o",
            str(output_path),
            "--doc-type",
            "report",
        ]
    else:  # generate-image
        cmd = [
            sys.executable,
            str(script_path),
            formatted_prompt,
            "--output",
            str(output_path),
        ]

    if verbose:
        print(f"  [生成] {filename}")
        print(f"        工具: {tool}")
        print(f"        提示: {formatted_prompt[:80]}...")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,  # 每张图像2分钟超时
        )

        if result.returncode == 0:
            if verbose:
                print(f"  [完成] {filename} 成功生成")
            return True
        else:
            print(f"  [错误] {filename} 失败:")
            if result.stderr:
                print(f"         {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"  [超时] {filename} 生成超时")
        return False
    except Exception as e:
        print(f"  [错误] {filename}: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="生成市场研究报告视觉内容（默认：5-6个核心视觉内容）"
    )
    parser.add_argument(
        "--topic", "-t", required=True, help="市场主题（例如：'电动汽车充电基础设施'）"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="figures",
        help="生成图像的输出目录（默认：figures）",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="生成所有27个扩展视觉内容（默认：仅核心5-6个）",
    )
    parser.add_argument(
        "--skip-existing", "-s", action="store_true", help="如果文件已存在则跳过生成"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    parser.add_argument(
        "--dry-run", action="store_true", help="显示将要生成的内容而不实际生成"
    )
    parser.add_argument(
        "--only", type=str, help="仅生成匹配此模式的视觉内容（例如：'01_'、'porter'）"
    )

    args = parser.parse_args()

    # 创建输出目录
    output_dir = Path(args.output_dir)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"市场研究视觉生成器")
    print(f"{'=' * 60}")
    print(f"主题: {args.topic}")
    print(f"输出目录: {output_dir.absolute()}")
    print(f"模式: {'所有视觉内容（27）' if args.all else '仅核心视觉内容（5-6）'}")
    print(f"跳过现有: {args.skip_existing}")
    print(f"{'=' * 60}\n")

    # 根据--all标志选择视觉集
    if args.all:
        visuals_to_generate = CORE_VISUALS + EXTENDED_VISUALS
        print("生成所有视觉内容（核心+扩展）\n")
    else:
        visuals_to_generate = CORE_VISUALS
        print("仅生成核心视觉内容（使用--all获取扩展集）\n")

    # 如果指定--only则过滤视觉内容
    if args.only:
        pattern = args.only.lower()
        visuals_to_generate = [
            v
            for v in visuals_to_generate
            if pattern in v[0].lower() or pattern in v[2].lower()
        ]
        print(f"过滤到{len(visuals_to_generate)}个匹配'{args.only}'的视觉内容\n")

    if args.dry_run:
        print("预运行 - 将生成以下视觉内容：\n")
        for filename, tool, prompt in visuals_to_generate:
            formatted = prompt.format(topic=args.topic)
            print(f"  {filename}")
            print(f"    工具: {tool}")
            print(f"    提示: {formatted[:60]}...")
            print()
        return

    # 生成所有视觉内容
    total = len(visuals_to_generate)
    success = 0
    failed = 0
    skipped = 0

    for i, (filename, tool, prompt) in enumerate(visuals_to_generate, 1):
        print(f"\n[{i}/{total}] 正在生成{filename}...")

        result = generate_visual(
            filename=filename,
            tool=tool,
            prompt=prompt,
            output_dir=output_dir,
            topic=args.topic,
            skip_existing=args.skip_existing,
            verbose=args.verbose,
        )

        if result:
            if args.skip_existing and (output_dir / filename).exists():
                skipped += 1
            else:
                success += 1
        else:
            failed += 1

    # 打印摘要
    print(f"\n{'=' * 60}")
    print(f"生成完成")
    print(f"{'=' * 60}")
    print(f"总计:    {total}")
    print(f"成功:    {success}")
    print(f"跳过:    {skipped}")
    print(f"失败:    {failed}")
    print(f"{'=' * 60}")

    if failed > 0:
        print(f"\n警告: {failed}个视觉内容生成失败。")
        print("查看上面的输出了解错误详情。")
        print("您可能需要手动生成失败的视觉内容。")

    print(f"\n输出目录: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
