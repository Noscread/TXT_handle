import os


def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print("错误: 文件未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
    return None

def read_file_line_by_line(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                print(line.strip())
    except FileNotFoundError:
        print("错误: 文件未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")

def read_file_remove_empty_lines(file_path):
    result = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line:
                    result.append(line)
        return result
    except FileNotFoundError:
        print("错误: 文件未找到!")
    except Exception as e:
        print(f"错误: 发生了一个未知错误: {e}")
    return []

def save_array_to_file(array, output_dir, output_filename):
    try:
        # 检查目录是否存在，不存在则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as file:
            for line in array:
                file.write(line + '\n')
        print(f"文件已成功保存到 {output_path}")
    except Exception as e:
        print(f"保存文件时出错: {e}")

if __name__ == "__main__":
    file_path = '测试.txt'

    # content = read_file(file_path)
    # if content is not None:
    #     print("文件内容如下:")
    #     print(content)

    # read_file_line_by_line(file_path)

    # content = read_file_remove_empty_lines(file_path)
    # print(content) # ["''", '1', '2', '""', '\'"'] 自动转义

    # content = read_file_remove_empty_lines(file_path)
    # if content:
    #     output_dir = 'content'
    #     output_filename = '测试.txt'
    #     save_array_to_file(content, output_dir, output_filename)