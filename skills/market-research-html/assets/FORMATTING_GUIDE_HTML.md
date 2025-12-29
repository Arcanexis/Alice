# 市场研究报告 HTML 格式指南 (Consulting Style)

本文档为 AI 生成专业市场研究报告提供 HTML 组件的使用标准。

## 1. 基础结构

每个报告应嵌套在 `.report-container` 中，并使用语义化标签：

```html
<div class="report-container">
    <section id="chapter-x">
        <h1>章节标题</h1>
        <p>正文内容...</p>
    </section>
</div>
```

## 2. 核心组件 (Boxes)

使用 `.box` 类配合特定类型类来实现侧边栏和高亮效果。

### 洞察框 (Insight Box) - 蓝色
用于展示核心发现、投资结论或深度洞察。
```html
<div class="insight-box box">
    <div class="box-title">关键洞察</div>
    <p>内容...</p>
</div>
```

### 数据框 (Data Box) - 绿色
用于展示市场快照、统计数据、关键指标（如 CAGR）。
```html
<div class="data-box box">
    <div class="box-title">市场快照</div>
    <ul>
        <li><b>指标：</b> 数据</li>
    </ul>
</div>
```

### 风险框 (Risk Box) - 橙色
用于列出潜在挑战、监管风险或市场阻力。
```html
<div class="risk-box box">
    <div class="box-title">主要风险</div>
    <p>内容...</p>
</div>
```

### 建议框 (Recommendation Box) - 紫色
用于列出具体的战略建议和行动计划。
```html
<div class="recommendation-box box">
    <div class="box-title">战略建议</div>
    <ol>
        <li>核心动作...</li>
    </ol>
</div>
```

## 3. 图表与表格 (Visuals & Tables)

### 图表容器
```html
<div class="figure">
    <img src="figures/image_name.png" alt="描述">
    <div class="caption"><b>图 X.Y：</b> 详细说明文本。<i>来源：[来源名称]</i></div>
</div>
```

### 专业表格
```html
<table>
    <thead>
        <tr>
            <th>分类</th>
            <th>数据 A</th>
            <th>数据 B</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>项目 1</td>
            <td>10%</td>
            <td>$100M</td>
        </tr>
    </tbody>
</table>
```

## 4. 打印与分页

- 每一个 `h1` 标签（即新章节开始）都会在打印时自动触发强制分页。
- 每一个 `section` 建议给定一个唯一的 `id`，方便进行定向编辑。
- 确保所有的图片路径使用相对路径 `figures/`。

## 5. 颜色规范参考

- **主色 (深蓝)：** `#003366` (用于标题、页眉、th)
- **次色 (中蓝)：** `#336699` (用于副标题)
- **强调绿：** `#008060` (用于数据增长)
- **警示红：** `#C62828` (用于高风险)
