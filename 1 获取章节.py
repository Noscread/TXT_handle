import re

def read_txt(file_path):
    """读取小说文件，整理正文、目录"""
    小说正文 = []
    小说目录 = []
    当前章节内容 = []
    第一章_found = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                # 正则表达式，匹配目录
                pattern = (r'(?:'
                           r'第[\s一二三四五六七八九十百千0-9]+(?:卷|章|节)' # \s 代表空格 ?: 代表非捕获组
                           r'|[0-9]+(?:\.|\．)' # 01.
                           r'|\([0-9]+\)'
                           r')')
                matches = re.findall(pattern, line)

                if matches:
                    if not 第一章_found:
                        第一章_found = True
                        if 当前章节内容:
                            小说正文.append(当前章节内容)
                            小说目录.append("前言")
                        当前章节内容 = [line]
                    else:
                        if 当前章节内容:
                            小说正文.append(当前章节内容)
                            小说目录.append(当前章节内容[0])
                        当前章节内容 = [line]
                else:
                    当前章节内容.append(line)

            # 处理最后一个章节
            if 当前章节内容:
                小说正文.append(当前章节内容)
                if 第一章_found:
                    小说目录.append(当前章节内容[0])
                else:
                    小说目录.append("前言")

        return {
            '小说正文': 小说正文,
            '小说目录': 小说目录
        }
    except FileNotFoundError:
        print("错误: 文件未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
    return {
        '小说正文': [],
        '小说目录': []
    }


if __name__ == "__main__":
    file_path = '测试.txt'
    contents = read_txt(file_path)
    print(contents.get('小说目录', '默认值'))
    # print(contents.get('小说正文', '默认值'))

    小说目录 = contents.get('小说目录', '')
    小说正文 = contents.get('小说正文', '')
    # print(小说目录[1])
    # print(小说正文[1])