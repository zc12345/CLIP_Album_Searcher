# README

## 命令行模式

这是一个简单的命令行工具，用于搜索指定文件夹中的图片。支持两种搜索方式：文本搜索和图像搜索。

### 用法
```python
python search.py --root_path <root_path> [--dump_path <dump_path>] [--backup_path <backup_path>] [--query <query>] [--image <image>] [--k <k>] [--threshold <threshold>]
```

### 参数
```
--root_path : 必需，指定要搜索的图片所在的文件夹的根路径。
--dump_path : 可选，指定图像特征向量的保存路径。默认为 db.pt。
--backup_path : 可选，指定备份特征向量的路径，每次重新运行如果检索到文件夹图片更新，会更新特征向量，并备份原先的特征向量。默认为 backup。
--query : 可选，指定要使用的文本查询。如果没有提供，则进行图像查询。
--image : 可选，指定要使用的图像查询。如果没有提供，则进行文本查询。
--k : 可选，指定返回的图像数量，k和threshold至少指定一个，k优先被使用。默认为 3。
--threshold : 可选，指定匹配阈值。默认为 None。
```

### 示例

#### 文本搜索
```python
python search.py --root_path D:\documents\images --query "cat" --k 5
```

#### 图像搜索
```python
python search.py --root_path D:\documents\images --image example.jpg --k 5
```

### 注意事项

* 第一次使用时会扫描整个文件夹并提取特征，会耗时比较久
* 当同时提供 `--query` 和 `--image` 参数时，只会执行 `--query` 参数。
在进行图像搜索时，搜索引擎会将输入图像与数据库中的图像进行比较，并返回与之最相似的图像。相似度通过余弦距离计算得出。

## webui模式

TODO