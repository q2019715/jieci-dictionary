# jieci-dictionary  
截词英语学习助手的Json词典  
词典来自于https://github.com/KyleBing/english-vocabulary   
我将其中的json版本使用本仓库中的 format_json.py 进行了一些格式化处理。   
词典是提供给https://github.com/q2019715/jieci 这个插件使用的。  


# 词库 JSON 格式说明

本文档描述插件可解析的词库 JSON 格式，以及字段合并规则。

# 示例
```json
{
    "word": "accrue",
    "phonetics": {
      "uk": "/əˈkɹuː/",
      "us": "/əˈkɹu/"
    },
    "translations": [
      {
        "type": "v",
        "translation": "积累"
      }
    ],
    "sentence_examples": [
      {
        "en": "And though pow’r fail’d, her Courage did accrue",
        "zh": "尽管力量衰退，她的勇气却在不断增长。"
      },
      {
        "en": "Environmental benefits that accrue to the area.",
        "zh": "归于该地区的环境收益。"
      }
    ]
  }
```
## 顶层结构

- 必须是 JSON 数组。
- 数组每一项是一个词条对象。
- 若顶层不是数组，导入会报错“词库格式不正确”。

示例：

```json
[
  {
    "word": "apple",
    "translations": [
      { "type": "n.", "translation": "苹果, 苹果树" },
      { "type": "adj.", "translation": "苹果味的" }
    ],
    "phrases": [
      { "phrase": "apple pie", "translations": ["苹果派"] },
      { "phrase": "an apple a day", "translation": "一天一苹果，医生远离我" }
    ]
  }
]
```

## 词条对象字段

### word

- 类型：字符串
- 用途：
    - en->cn 模式：作为英文索引 key（会转小写）。
    - cn->en 模式：作为显示的英文词。

### phonetics
- 类型：对象（可选）
- 字段：
  - `uk`：英式音标字符串
  - `us`：美式音标字符串
- 用途：用于在词条中展示发音信息。
  示例：
```json
{
  "phonetics": {
    "uk": "/əbˈzɔːb/",
    "us": "/əˈbɹʌp.li/"
  }
}
```

### translations

- 类型：数组
- 每项对象结构：
    - `type`：词性/类型（可为空字符串）
    - `translation`：翻译字符串
- `translation` 会按 `,`、`，`、`、` 等分隔，拆成多个义项。

示例：

```json
{
  "translations": [
    { "type": "n.", "translation": "苹果, 苹果树" }
  ]
}
```

### phrases

- 类型：数组（可选）
- 每项对象最少包含：
    - `phrase`：短语文本
- 翻译字段支持多种写法，解析时会合并：
    - 数组字段：`translations`、`trans`、`meanings`
    - 字符串字段：`translation`、`trans`

示例：

```json
{
  "phrases": [
    { "phrase": "apple pie", "translations": ["苹果派"] },
    { "phrase": "an apple a day", "translation": "一天一苹果，医生远离我" }
  ]
}
```


### sentence_examples

- 类型：数组（可选）
- 每项对象结构：
    - en：英文例句
    - zh：中文翻译
- 用途：用于展示词条的例句和对应翻译。
```json
{
"sentence_examples": [
{
"en": "The professor stopped her lecture abruptly when she noticed someone fall off their seat.",
"zh": "当她注意到有人从座位上摔下来时，教授突然中断了她的讲座。"
}
]
}
```



# 关于这个数据集是如何制作的
1、https://github.com/KyleBing/english-vocabulary   从这里下载  
2、使用脚本(\tools\q2019_format_json.py)进行格式转化