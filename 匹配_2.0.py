import re
import os
import shutil
import tkinter as tk
from tkinter import filedialog, Text

media_type = ('.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.iso', '.mpg', '.m4v')
sub_type = ('.smi', '.srt', '.idx', '.sub', '.sup', '.psb', '.ssa', '.ass', '.usf', '.xss', '.ssf', '.rt', '.lrc', '.sbv', '.vtt', '.ttml')

def find_files(extension_tuple, directory):
    """查找指定目录及其子目录下的所有特定扩展名的文件。"""
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extension_tuple):
                yield os.path.join(dirpath, filename)
                
def extract_feature_code(filename):
    """从文件名中提取特征码"""
    fc2_pattern = re.compile(r"(FC2-?PPV?-?(\d+))", re.I)
    general_pattern = re.compile(r"(\w+[-_ ]\w+)", re.I)  # 修改正则以匹配中间的空格
    
    match_fc2 = fc2_pattern.search(filename)
    match_general = general_pattern.search(filename)
    
    if match_fc2:
        return f"FC2-{match_fc2.group(2)}"
    elif match_general:
        return match_general.group(1).replace(" ", "-").replace("_", "-")
    else:
        return None

def video_is_subtitled(filename):
    """检查视频文件名是否表示它已经有字幕。"""
    return re.search(r'-c(-[^ \.-]+)?(\.[a-z0-9]+)?$', filename, re.I) is not None

def match_and_copy_subs(video_directory, subtitle_directory, output_text_widget):
    """匹配字幕和视频文件，并模拟复制字幕到视频目录。"""
    video_files = list(find_files(media_type, video_directory))
    subtitle_files = list(find_files(sub_type, subtitle_directory))

    video_features = {}
    for v in video_files:
        if not video_is_subtitled(os.path.basename(v)):
            feature_code = extract_feature_code(os.path.basename(v))
            if feature_code not in video_features:  # 只存储第一个匹配到的特征码的文件
                video_features[feature_code] = v

    subtitle_features = {}
    for s in subtitle_files:
        feature_code = extract_feature_code(os.path.basename(s))
        if feature_code not in subtitle_features:  # 同样，只存储第一个匹配到的特征码的文件
            subtitle_features[feature_code] = s

    matched_count = 0

    for sub_feature, sub_path in subtitle_features.items():
        if not sub_feature:  # 跳过特征码为None的匹配
            continue
        video_path = video_features.get(sub_feature)
        if video_path:
            target_dir = os.path.dirname(video_path)
            shutil.copy(sub_path, target_dir) 
            output_text_widget.insert(tk.END, f"特征码: [{sub_feature}] 匹配成功！\n复制字幕 {sub_path} \n到 {target_dir}\n\n")
            matched_count += 1

    # 输出匹配结束的信息
    output_text_widget.insert(tk.END, f"匹配结束！\n字幕文件数量: {len(subtitle_files)}\n视频文件数量: {len(video_files)}\n匹配成功的数量: {matched_count}\n\n")




def browse_directory():
    """弹出目录选择窗口并返回所选目录。"""
    return filedialog.askdirectory()

def main():
    root = tk.Tk()
    root.title("字幕视频匹配工具")

    tk.Label(root, text="字幕库文件目录地址：").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    subtitle_dir_var = tk.StringVar()
    tk.Entry(root, textvariable=subtitle_dir_var, width=40).grid(row=0, column=1)
    tk.Button(root, text="浏览", command=lambda: subtitle_dir_var.set(browse_directory())).grid(row=0, column=2, padx=10)

    tk.Label(root, text="视频库文件目录地址：").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
    video_dir_var = tk.StringVar()
    tk.Entry(root, textvariable=video_dir_var, width=40).grid(row=1, column=1)
    tk.Button(root, text="浏览", command=lambda: video_dir_var.set(browse_directory())).grid(row=1, column=2, padx=10)

    tk.Button(root, text="开始匹配", command=lambda: match_and_copy_subs(video_dir_var.get(), subtitle_dir_var.get(), output_text)).grid(row=2, columnspan=3, pady=10)

    # 建立滚动条
    scrollbar = tk.Scrollbar(root)
    scrollbar.grid(row=3, column=3, sticky='ns')

    output_text = Text(root, height=30, width=60, yscrollcommand=scrollbar.set)  # yscrollcommand设置为滚动条的set方法
    output_text.grid(row=3, columnspan=3, padx=10, pady=(10,20))

    # 配置滚动条的command为Text部件的yview方法
    scrollbar.config(command=output_text.yview)

    root.mainloop()


if __name__ == "__main__":
    main()