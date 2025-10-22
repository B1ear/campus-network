"""
网络配置管理模块
提供默认配置和可配置的网络参数
"""

DEFAULT_CONFIG = {
    "num_nodes": 25,           # 路由器数量
    "cost_range": [10, 100],   # 造价范围
    "capacity_range": [100, 1000],  # 吞吐量/容量范围
    "seed": 42                 # 随机种子
}


class NetworkConfig:
    """网络配置类"""
    
    def __init__(self, **kwargs):
        """
        初始化网络配置
        
        Args:
            num_nodes: 路由器数量
            cost_range: 造价范围 [min, max]
            capacity_range: 容量范围 [min, max]
            seed: 随机种子
        """
        self.num_nodes = kwargs.get('num_nodes', DEFAULT_CONFIG['num_nodes'])
        self.cost_range = kwargs.get('cost_range', DEFAULT_CONFIG['cost_range'])
        self.capacity_range = kwargs.get('capacity_range', DEFAULT_CONFIG['capacity_range'])
        self.seed = kwargs.get('seed', DEFAULT_CONFIG['seed'])
        
        # 验证配置
        self._validate()
    
    def _validate(self):
        """验证配置参数的有效性"""
        if self.num_nodes < 2:
            raise ValueError("节点数必须至少为2")
        if len(self.cost_range) != 2 or self.cost_range[0] >= self.cost_range[1]:
            raise ValueError("造价范围格式错误")
        if len(self.capacity_range) != 2 or self.capacity_range[0] >= self.capacity_range[1]:
            raise ValueError("容量范围格式错误")
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'num_nodes': self.num_nodes,
            'cost_range': self.cost_range,
            'capacity_range': self.capacity_range,
            'seed': self.seed
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建配置对象"""
        return cls(**data)
    
    @classmethod
    def default(cls):
        """获取默认配置"""
        return cls(**DEFAULT_CONFIG)
