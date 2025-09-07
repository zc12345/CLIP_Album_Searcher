// 随机文本生成器 - 使用模板和随机组合生成有意义的文本
export class RandomTextGenerator {
  constructor() {
    // 主题模板
    this.themes = [
      '自然风景', '动物世界', '城市建筑', '美食餐饮', 
      '人物肖像', '交通工具', '节日庆典', '体育运动',
      '艺术创作', '科技产品', '日常生活', '历史文化'
    ]

    // 形容词库
    this.adjectives = [
      '美丽的', '壮观的', '可爱的', '精彩的', '迷人的', '优雅的', 
      '雄伟的', '精致的', '浪漫的', '神秘的', '现代的', '传统的',
      '热闹的', '宁静的', '鲜艳的', '柔和的', '动态的', '静态的',
      '阳光明媚的', '月光下的', '雨中的', '雪后的', '清晨的', '黄昏的'
    ]

    // 名词库 - 按主题分类
    this.nounsByTheme = {
      '自然风景': ['山脉', '湖泊', '海洋', '森林', '河流', '瀑布', '沙漠', '草原', '花园', '公园'],
      '动物世界': ['小猫', '小狗', '小鸟', '蝴蝶', '金鱼', '熊猫', '狮子', '大象', '海豚', '鲸鱼'],
      '城市建筑': ['摩天大楼', '古老教堂', '现代桥梁', '历史遗迹', '商业街区', '居民小区', '火车站', '机场', '博物馆', '图书馆'],
      '美食餐饮': ['美味蛋糕', '新鲜水果', '精致料理', '传统小吃', '烘焙面包', '冰淇淋', '咖啡', '茶饮', '海鲜大餐', '烧烤'],
      '人物肖像': ['微笑的孩子', '优雅的女性', '帅气的男性', '慈祥的老人', '亲密的情侣', '欢乐的家庭', '专业的模特', '传统文化的表演者'],
      '交通工具': ['豪华跑车', '经典摩托车', '彩色自行车', '大型客机', '高速列车', '豪华游轮', '复古公交车', '帆船', '热气球'],
      '节日庆典': ['春节庆祝', '圣诞装饰', '婚礼现场', '生日派对', '音乐节', '文化节', '烟花表演', '游行队伍', '传统舞蹈'],
      '体育运动': ['足球比赛', '篮球运动员', '游泳选手', '跑步比赛', '瑜伽练习', '滑雪运动', '冲浪高手', '体操表演', '拳击比赛'],
      '艺术创作': ['油画作品', '水彩画', '雕塑艺术', '摄影作品', '街头涂鸦', '数字艺术', '传统书法', '手工艺品', '时装设计'],
      '科技产品': ['智能手机', '笔记本电脑', '无人机', '机器人', '虚拟现实', '智能家居', '电动汽车', '数码相机', '游戏设备'],
      '日常生活': ['早晨咖啡', '午后阅读', '夜晚散步', '周末购物', '家庭聚餐', '朋友聚会', '工作场景', '学习时刻', '休闲时光'],
      '历史文化': ['古代建筑', '传统服饰', '历史文物', '文化仪式', '民间艺术', '古老街道', '博物馆展品', '考古发现', '传统节日']
    }

    // 动作和场景库
    this.actions = [
      '正在玩耍', '在奔跑', '在飞翔', '在游泳', '在休息', '在进食', 
      '在工作', '在表演', '在比赛', '在庆祝', '在旅行', '在创作',
      '在思考', '在微笑', '在跳舞', '在唱歌', '在阅读', '在烹饪'
    ]

    this.locations = [
      '在草地上', '在沙滩上', '在山顶上', '在湖边', '在森林中', '在城市里',
      '在公园里', '在家中', '在餐厅里', '在舞台上', '在赛场上', '在街道上',
      '在海边', '在雨中', '在雪中', '在阳光下', '在月光下', '在星空下'
    ]

    // 高级描述词
    this.descriptors = [
      '特写镜头', '广角视角', '微距摄影', '黑白照片', '彩色照片', 
      '高对比度', '柔光效果', '逆光拍摄', '黄金时刻', '蓝色时刻',
      '充满活力', '宁静祥和', '热闹非凡', '浪漫氛围', '神秘感'
    ]
  }

  // 生成随机文本
  generate() {
    const theme = this.getRandomItem(this.themes)
    const templateType = Math.random() > 0.5 ? 'descriptive' : 'scenic'
    
    let text = ''
    
    if (templateType === 'descriptive') {
      text = this.generateDescriptiveText(theme)
    } else {
      text = this.generateScenicText(theme)
    }

    // 50%几率添加高级描述
    if (Math.random() > 0.5) {
      text += `，${this.getRandomItem(this.descriptors)}`
    }

    return text
  }

  // 生成描述性文本
  generateDescriptiveText(theme) {
    const adjective = this.getRandomItem(this.adjectives)
    const noun = this.getRandomItem(this.nounsByTheme[theme] || this.nounsByTheme['自然风景'])
    
    // 70%几率添加动作或场景
    if (Math.random() > 0.3) {
      if (Math.random() > 0.5) {
        const action = this.getRandomItem(this.actions)
        return `${adjective}${noun}${action}`
      } else {
        const location = this.getRandomItem(this.locations)
        return `${adjective}${noun}${location}`
      }
    }
    
    return `${adjective}${noun}`
  }

  // 生成场景文本
  generateScenicText(theme) {
    const elements = []
    const numElements = Math.floor(Math.random() * 2) + 2 // 2-3个元素
    
    for (let i = 0; i < numElements; i++) {
      const adjective = this.getRandomItem(this.adjectives)
      const noun = this.getRandomItem(this.nounsByTheme[theme] || this.nounsByTheme['自然风景'])
      elements.push(`${adjective}${noun}`)
    }
    
    return elements.join('和')
  }

  // 获取随机数组元素
  getRandomItem(array) {
    return array[Math.floor(Math.random() * array.length)]
  }

  // 批量生成文本
  generateMultiple(count) {
    const results = []
    for (let i = 0; i < count; i++) {
      results.push(this.generate())
    }
    return results
  }
}

// 创建单例实例
export const textGenerator = new RandomTextGenerator()