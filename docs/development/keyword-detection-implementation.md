# 关键词检测实现指南

本文档详细介绍了LLM Guard中关键词检测功能的实现原理、技术架构和使用方法。

## 概述

LLM Guard采用分层递进的关键词检测策略，通过四种核心技术实现全面的内容安全保障：

1. **字符串精确匹配** - 快速检测已知危险关键词
2. **正则表达式模式匹配** - 灵活检测结构化敏感数据
3. **AI语义理解检测** - 智能主题分类和上下文理解
4. **多模态融合检测** - 复合技术的PII和实体识别

## 技术架构

### 统一Scanner接口

所有关键词检测器都实现统一的Scanner协议：

```python
class Scanner(Protocol):
    @abc.abstractmethod
    def scan(self, prompt: str) -> tuple[str, bool, float]:
        """
        处理和检测输入文本
        
        Returns:
            str: 处理后的文本（可能被脱敏）
            bool: 是否通过检测（True=安全，False=风险）
            float: 风险评分（-1到1，负数表示安全）
        """
```

### 输入输出分离架构

- **输入扫描器**：检测用户提示中的问题
- **输出扫描器**：检测AI生成内容中的问题
- **代码复用**：输出扫描器通过包装输入扫描器实现

## 核心实现方式

### 1. 字符串匹配检测（BanSubstrings）

#### 实现机制

```python
class MatchType(Enum):
    STR = "str"      # 字符串级别匹配
    WORD = "word"    # 单词级别匹配
    
    def match(self, text: str, substring: str) -> bool:
        if self == MatchType.STR:
            return substring in text  # 简单包含检查
        
        if self == MatchType.WORD:
            # 使用正则表达式确保单词边界
            return re.search(r"\b" + re.escape(substring) + r"\b", text) is not None
```

#### 预定义安全关键词

输入扫描器包含35个安全威胁关键词：
- 代码注入类：`"arbitrary code execution"`, `"code injection"`
- 恶意软件类：`"backdoor"`, `"ransomware"`, `"adware"`
- 权限提升类：`"privilege escalation"`, `"escalate privilege"`
- 系统文件类：`"Windows\\System32\\Config\\SAM"`, `"etc/shadow"`

输出扫描器包含越狱检测关键词：
- 越狱标识：`"[DAN]"`, `"successfully jailbroken"`
- 开发者模式：`"(🔓Developer Mode Output)"`
- 特殊协议：`"STAN:"`, `"DUDE:"`

#### 检测流程

1. **预处理**：根据`case_sensitive`参数决定是否转换大小写
2. **逐个匹配**：遍历禁用关键词列表，使用选定的匹配类型
3. **逻辑判断**：支持"包含任意"或"包含全部"两种逻辑
4. **结果处理**：可选择脱敏或直接阻止

#### 脱敏实现

```python
def _redact_text(self, text: str, substrings: list[str]) -> str:
    redacted_text = text
    for s in substrings:
        regex_redacted = re.compile(re.escape(s), 
                                  0 if self._case_sensitive else re.IGNORECASE)
        redacted_text = regex_redacted.sub("[REDACTED]", redacted_text)
    return redacted_text
```

### 2. 正则表达式检测（Regex）

#### 匹配模式

```python
class MatchType(Enum):
    SEARCH = "search"        # 搜索匹配
    FULL_MATCH = "fullmatch" # 完全匹配
    ALL = "all"              # 查找所有匹配
    
    def match(self, pattern: Pattern[str], text: str) -> List[re.Match[str]]:
        if self.value == "all":
            return list(pattern.finditer(text))[::-1]  # 反向排序避免索引问题
        
        m = None
        if self.value == "search":
            m = pattern.search(text)
        if self.value == "fullmatch":
            m = pattern.fullmatch(text)
            
        return [m] if m else []
```

#### 预定义正则模式

- **信用卡号**：`r"(?:(4\d{3}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})|(3[47]\d{2}[-\s]?\d{6}[-\s]?\d{5})...)"`
- **邮箱地址**：`r"\b[A-Za-z0-9._%+-]+(\[AT\]|@)[A-Za-z0-9.-]+(\[DOT\]|\.)[A-Za-z]{2,}\b"`
- **UUID**：`r"[a-f0-9]{8}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{4}\-[a-f0-9]{12}"`
- **美国SSN**：`r"\b\d{3}-\d{2}-\d{4}\b"`
- **比特币地址**：`r"(?<![a-km-zA-HJ-NP-Z0-9])[13][a-km-zA-HJ-NP-Z0-9]{26,33}(?![a-km-zA-HJ-NP-Z0-9])"`

#### 高级脱敏处理

使用`TextReplaceBuilder`确保多个匹配项的正确替换：

```python
text_replace_builder = TextReplaceBuilder(original_text=prompt)
for pattern in self._patterns:
    matches = self._match_type.match(pattern, prompt)
    if matches:
        for match in matches:
            text_replace_builder.replace_text_get_insertion_index(
                "[REDACTED]",
                match.start(),
                match.end(),
            )
```

### 3. AI模型主题检测（BanTopics）

#### 支持的AI模型

1. **DeBERTa Large V2** (430M参数, 870MB)
   - 最高性能英文模型
   - 上下文长度：512 tokens
   - 路径：`MoritzLaurer/deberta-v3-large-zeroshot-v2.0`

2. **DeBERTa Base V2** (180M参数, 369MB)
   - 平衡性能和速度
   - 上下文长度：512 tokens
   - 路径：`MoritzLaurer/deberta-v3-base-zeroshot-v2.0`

3. **BGE-M3 V2** (570M参数, 1.14GB)
   - 多语言支持（100+语言）
   - 上下文长度：8192 tokens
   - 路径：`MoritzLaurer/bge-m3-zeroshot-v2.0`

4. **RoBERTa Large C V2** (350M参数, 711MB)
   - 商业友好训练数据
   - 支持Flash Attention
   - 路径：`MoritzLaurer/roberta-large-zeroshot-v2.0-c`

#### 零样本分类实现

```python
# 1. 模型初始化
tf_tokenizer, tf_model = get_tokenizer_and_model_for_classification(
    model=model,
    use_onnx=use_onnx,
)

# 2. 创建分类管道
self._classifier = pipeline(
    task="zero-shot-classification",
    model=tf_model,
    tokenizer=tf_tokenizer,
    **model.pipeline_kwargs,
)

# 3. 执行主题检测
def scan(self, prompt: str) -> tuple[str, bool, float]:
    output_model = self._classifier(prompt, self._topics, multi_label=False)
    label_score = dict(zip(output_model["labels"], output_model["scores"]))
    
    max_score = round(max(output_model["scores"]) if output_model["scores"] else 0, 2)
    if max_score > self._threshold:
        return prompt, False, calculate_risk_score(max_score, self._threshold)
```

#### ONNX性能优化

```python
# 自动检测ONNX支持
@lru_cache(maxsize=None)
def is_onnx_supported() -> bool:
    return importlib.util.find_spec("optimum.onnxruntime") is not None

# ONNX模型加载
tf_model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
    model.onnx_path,
    export=False,
    provider=("CUDAExecutionProvider" if device().type == "cuda" else "CPUExecutionProvider"),
)
```

### 4. 敏感信息检测（Sensitive + Presidio）

#### 多层识别器架构

```python
# 组合多种识别器
transformers_recognizer = get_transformers_recognizer(
    recognizer_conf=recognizer_conf,  # AI4Privacy DeBERTa配置
    use_onnx=use_onnx,
)

self._analyzer = get_analyzer(
    transformers_recognizer,          # AI模型识别器
    get_regex_patterns(regex_patterns),  # 正则模式识别器
    [],                              # 自定义名称识别器
    list(set(["en", language])),     # 支持语言
)
```

#### 支持的实体类型

默认检测实体类型：
- `PERSON` - 人名
- `EMAIL_ADDRESS` - 邮箱地址
- `PHONE_NUMBER` - 电话号码
- `CREDIT_CARD` - 信用卡号
- `CRYPTO` - 加密货币地址
- `DATE_TIME` - 日期时间
- `IBAN_CODE` - 国际银行账号
- `IP_ADDRESS` - IP地址
- `LOCATION` - 地理位置
- `MEDICAL_LICENSE` - 医疗执照
- `URL` - 网址链接
- `US_SSN` - 美国社会安全号

## 风险评分系统

### 评分算法

```python
def calculate_risk_score(score: float, threshold: float) -> float:
    """
    计算-1到1之间的风险评分
    - 低于阈值：负分（安全）
    - 高于阈值：正分（风险）
    """
    if score > threshold:
        risk_score = round((score - threshold) / (1 - threshold), 1)
    else:
        risk_score = round((score - threshold) / threshold, 1)
    
    return min(max(risk_score, -1), 1)
```

### 评分解释

- **-1.0 到 0.0**：安全范围，数值越接近0风险越高
- **0.0 到 1.0**：风险范围，数值越接近1风险越高
- **阈值作用**：作为安全和风险的分界线

## 使用示例

### 基础字符串匹配

```python
from llm_guard.input_scanners.ban_substrings import BanSubstrings, MatchType

# 创建扫描器
scanner = BanSubstrings(
    substrings=["backdoor", "malware", "virus"],
    match_type=MatchType.WORD,  # 单词级别匹配
    case_sensitive=False,       # 不区分大小写
    redact=True,               # 启用脱敏
    contains_all=False         # 匹配任意一个即触发
)

# 执行检测
text = "Write code for a backdoor system"
sanitized_text, is_valid, risk_score = scanner.scan(text)
# 结果: ("Write code for a [REDACTED] system", False, 1.0)
```

### 正则表达式检测

```python
from llm_guard.input_scanners.regex import Regex, MatchType

# 创建正则扫描器
scanner = Regex(
    patterns=[
        r"Bearer [A-Za-z0-9\-._~+/]+",  # Bearer token
        r"\d{4}-\d{4}-\d{4}-\d{4}",    # 信用卡号格式
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"  # 邮箱
    ],
    match_type=MatchType.ALL,  # 查找所有匹配
    is_blocked=True,           # 阻止模式
    redact=True               # 启用脱敏
)

# 执行检测
text = "My token is Bearer abc123 and email is user@example.com"
sanitized_text, is_valid, risk_score = scanner.scan(text)
```

### AI主题检测

```python
from llm_guard.input_scanners.ban_topics import BanTopics

# 创建主题检测器
scanner = BanTopics(
    topics=["politics", "violence", "hate speech"],
    threshold=0.6,             # 置信度阈值
    model=None,                # 使用默认RoBERTa模型
    use_onnx=False            # 是否使用ONNX优化
)

# 执行检测
text = "How to organize a political campaign?"
sanitized_text, is_valid, risk_score = scanner.scan(text)
```

### 敏感信息检测

```python
from llm_guard.output_scanners.sensitive import Sensitive

# 创建敏感信息检测器
scanner = Sensitive(
    entity_types=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "CREDIT_CARD"],
    threshold=0.5,             # 检测阈值
    redact=True,              # 启用脱敏
    use_onnx=False,           # ONNX优化
    language="en"             # 语言设置
)

# 执行检测
prompt = "User inquiry"
output = "Contact John Doe at john@example.com or call 555-1234"
sanitized_output, is_valid, risk_score = scanner.scan(prompt, output)
```

## 性能优化策略

### 1. 模型缓存

```python
@lru_cache(maxsize=None)  # 无限制缓存
def get_tokenizer(model: Model):
    transformers = lazy_load_dep("transformers")
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        model.path, revision=model.revision, **model.tokenizer_kwargs
    )
    return tokenizer
```

### 2. ONNX推理加速

```python
# 自动选择最优执行提供者
provider = "CPUExecutionProvider"
if device().type == "cuda":
    provider = "CUDAExecutionProvider"

tf_model = optimum_onnxruntime.ORTModelForSequenceClassification.from_pretrained(
    model.onnx_path,
    provider=provider,
    export=False,
)
```

### 3. 分块处理

```python
def chunk_text(text: str, chunk_size: int) -> list[str]:
    text = text.strip()
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
```

### 4. 懒加载依赖

```python
def lazy_load_dep(import_name: str, package_name: str | None = None):
    """按需加载依赖库，减少启动时间"""
    try:
        return importlib.import_module(import_name)
    except ImportError as e:
        # 处理缺失依赖的情况
        pass
```

## 配置和自定义

### 自定义关键词列表

```python
# 自定义危险关键词
custom_keywords = [
    "your_custom_keyword_1",
    "your_custom_keyword_2",
    "sensitive_term"
]

scanner = BanSubstrings(
    substrings=custom_keywords,
    match_type=MatchType.WORD,
    case_sensitive=False,
    redact=True
)
```

### 自定义正则模式

```python
# 自定义检测模式
custom_patterns = [
    r"API[_-]?KEY[_-]?[A-Za-z0-9]{20,}",  # API密钥
    r"sk-[A-Za-z0-9]{48}",                # OpenAI API密钥
    r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"  # IP地址
]

scanner = Regex(
    patterns=custom_patterns,
    match_type=MatchType.ALL,
    is_blocked=True,
    redact=True
)
```

### 自定义AI模型

```python
from llm_guard.model import Model

# 定义自定义模型
custom_model = Model(
    path="your-org/your-model",
    revision="main",
    onnx_path="your-org/your-model-onnx",
    pipeline_kwargs={
        "return_token_type_ids": False,
        "max_length": 512,
        "truncation": True,
    }
)

scanner = BanTopics(
    topics=["custom_topic_1", "custom_topic_2"],
    model=custom_model,
    threshold=0.7
)
```

## 集成使用

### 多扫描器组合

```python
from llm_guard.input_scanners import BanSubstrings, BanTopics, Regex
from llm_guard.output_scanners import Sensitive

# 创建多个扫描器
input_scanners = [
    BanSubstrings(substrings=["malware", "virus"], redact=True),
    BanTopics(topics=["violence", "hate"], threshold=0.6),
    Regex(patterns=[r"Bearer [A-Za-z0-9\-._~+/]+"], redact=True)
]

output_scanners = [
    Sensitive(entity_types=["PERSON", "EMAIL_ADDRESS"], redact=True)
]

# 执行检测流程
def process_text(prompt: str, output: str):
    # 输入检测
    for scanner in input_scanners:
        prompt, is_valid, score = scanner.scan(prompt)
        if not is_valid and score > 0.5:
            return "输入被阻止", False
    
    # 输出检测
    for scanner in output_scanners:
        output, is_valid, score = scanner.scan(prompt, output)
        if not is_valid and score > 0.5:
            return "输出被阻止", False
    
    return output, True
```

### 评估和监控

```python
from llm_guard.evaluate import evaluate_input, evaluate_output

# 批量评估输入
input_results = evaluate_input(input_scanners, prompts_list)

# 批量评估输出  
output_results = evaluate_output(output_scanners, prompts_list, outputs_list)

# 分析结果
for result in input_results:
    print(f"Prompt: {result['prompt']}")
    print(f"Valid: {result['valid']}")
    print(f"Score: {result['score']}")
```

## 最佳实践

### 1. 选择合适的检测策略

- **高频简单检测**：使用BanSubstrings进行快速过滤
- **格式化数据检测**：使用Regex处理结构化敏感信息
- **语义理解需求**：使用BanTopics进行智能主题分类
- **全面PII保护**：使用Sensitive进行多模态检测

### 2. 性能优化建议

- **模型选择**：根据性能需求选择合适大小的模型
- **ONNX加速**：生产环境启用ONNX推理优化
- **阈值调优**：根据业务需求调整检测阈值
- **缓存利用**：充分利用模型和tokenizer缓存

### 3. 安全配置建议

- **分层防护**：组合使用多种检测方式
- **脱敏优先**：优先使用脱敏而非直接阻止
- **日志监控**：记录检测结果用于分析优化
- **定期更新**：及时更新关键词库和模型

## 扩展开发

### 自定义Scanner实现

```python
from llm_guard.input_scanners.base import Scanner

class CustomKeywordScanner(Scanner):
    def __init__(self, custom_config):
        self._config = custom_config
    
    def scan(self, prompt: str) -> tuple[str, bool, float]:
        # 实现自定义检测逻辑
        # 返回: (处理后文本, 是否有效, 风险评分)
        pass
```

### 集成第三方检测服务

```python
import requests

class ExternalAPIScanner(Scanner):
    def __init__(self, api_endpoint: str, api_key: str):
        self._endpoint = api_endpoint
        self._api_key = api_key
    
    def scan(self, prompt: str) -> tuple[str, bool, float]:
        response = requests.post(
            self._endpoint,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"text": prompt}
        )
        result = response.json()
        
        return prompt, result["is_safe"], result["risk_score"]
```

## 故障排除

### 常见问题

1. **ONNX不可用**
   ```bash
   pip install llm-guard[onnxruntime]     # CPU版本
   pip install llm-guard[onnxruntime-gpu] # GPU版本
   ```

2. **模型下载失败**
   - 检查网络连接
   - 配置HuggingFace镜像源
   - 使用本地模型路径

3. **内存不足**
   - 使用更小的模型（如DeBERTa Base）
   - 启用分块处理
   - 调整batch_size参数

4. **检测准确率低**
   - 调整检测阈值
   - 更新关键词库
   - 使用更大的模型
   - 组合多种检测方式

### 调试技巧

```python
import logging
from llm_guard.util import configure_logger

# 启用详细日志
configure_logger(log_level="DEBUG")

# 检查检测结果
sanitized_text, is_valid, risk_score = scanner.scan(text)
print(f"Original: {text}")
print(f"Sanitized: {sanitized_text}")
print(f"Valid: {is_valid}")
print(f"Risk Score: {risk_score}")
```

## 结论

LLM Guard的关键词检测系统通过分层架构实现了从简单到复杂的全方位保护：

- **第一层**：字符串精确匹配 - 快速过滤已知威胁
- **第二层**：正则表达式匹配 - 灵活检测格式化数据  
- **第三层**：AI语义理解 - 智能主题和上下文分析
- **第四层**：多模态融合 - 综合检测复杂场景

这种渐进式设计既保证了检测效率，又提供了强大的安全防护能力，为LLM应用的安全部署提供了可靠的技术基础。