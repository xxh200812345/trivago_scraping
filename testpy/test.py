class Singleton:
    _instance = None  # 初始化类变量，用于存储实例

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:  # 使用is None来进行检查
            cls._instance = super(Singleton, cls).__new__(cls)  # 创建实例
            cls._instance.data()
        return cls._instance  # 返回已存在的实例
    
    def data(self):
        print("init")
# 示例使用
instance1 = Singleton()
instance2 = Singleton()

print(instance1 is instance2)  # 输出 True，说明instance1和instance2是同一个实例
