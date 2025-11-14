import os
import yaml

# 获取当前文件的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取config目录以及project_config.yaml文件的路径
CONFIG_PATH = os.path.join(CURRENT_DIR, "..", "config", "project_config.yaml")

def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# 加载配置为全局变量
CURRENT_PROJECT = load_yaml_config(CONFIG_PATH)
