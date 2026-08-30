# -*- coding: utf-8 -*-
import os
import re
import base64
import sys

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"D:\菩提缘\新鲜人"
html_path = os.path.join(BASE_DIR, "倒放挑战.html")
output_path = os.path.join(BASE_DIR, "倒放挑战_单文件版.html")

def embed_assets():
    if not os.path.exists(html_path):
        print(f"错误: 找不到 HTML 文件: {html_path}")
        return

    print("开始打包单网页文件，正在读取 HTML...")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 嵌入背景图片 background.jpeg
    bg_path = os.path.join(BASE_DIR, "background.jpeg")
    if os.path.exists(bg_path):
        print("正在编码背景图片...")
        with open(bg_path, "rb") as img_f:
            bg_base64 = base64.b64encode(img_f.read()).decode("utf-8")
        content = content.replace("url('background.jpeg')", f"url('data:image/jpeg;base64,{bg_base64}')")
        content = content.replace('url("background.jpeg")', f'url("data:image/jpeg;base64,{bg_base64}")')
        print("✅ 已成功嵌入背景图片 background.jpeg")
    else:
        print("⚠️ 未找到背景图片 background.jpeg，跳过嵌入")

    # 2. 匹配并嵌入所有音频文件
    audio_pattern = r'["\'](原音频/[^"\']+\.mp3|倒放音频/[^"\']+\.mp3)["\']'
    matches = re.findall(audio_pattern, content)
    
    unique_matches = set(matches)
    embedded_count = 0
    
    for relative_path in unique_matches:
        normalized_rel_path = relative_path.replace("/", os.sep)
        full_path = os.path.join(BASE_DIR, normalized_rel_path)
        
        if os.path.exists(full_path):
            print(f"正在编码音频: {relative_path} ...")
            with open(full_path, "rb") as audio_f:
                audio_base64 = base64.b64encode(audio_f.read()).decode("utf-8")
            
            data_url = f"data:audio/mp3;base64,{audio_base64}"
            # 替换 HTML 中的相对路径
            content = content.replace(f'"{relative_path}"', f'"{data_url}"')
            content = content.replace(f"'{relative_path}'", f"'{data_url}'")
            embedded_count += 1
        else:
            print(f"❌ 未找到音频文件: {full_path}")

    print(f"✅ 共成功嵌入 {embedded_count} 个音频文件")

    # 3. 匹配并嵌入所有歌曲封面图片
    image_pattern = r'["\'](image/[^"\']+\.(?:jpg|jpeg|png|webp))["\']'
    img_matches = re.findall(image_pattern, content)
    
    unique_img_matches = set(img_matches)
    embedded_img_count = 0
    
    for relative_path in unique_img_matches:
        normalized_rel_path = relative_path.replace("/", os.sep)
        full_path = os.path.join(BASE_DIR, normalized_rel_path)
        
        if os.path.exists(full_path):
            print(f"正在编码封面图片: {relative_path} ...")
            ext = os.path.splitext(relative_path)[1].lower().strip(".")
            mime_type = "jpeg" if ext in ["jpg", "jpeg"] else ext
            
            with open(full_path, "rb") as img_f:
                img_base64 = base64.b64encode(img_f.read()).decode("utf-8")
            
            data_url = f"data:image/{mime_type};base64,{img_base64}"
            # 替换 HTML 中的相对路径
            content = content.replace(f'"{relative_path}"', f'"{data_url}"')
            content = content.replace(f"'{relative_path}'", f"'{data_url}'")
            embedded_img_count += 1
        else:
            print(f"⚠️ 未找到封面图片: {full_path} (运行网页时将自动显示默认🎵图标)")

    print(f"✅ 共成功嵌入 {embedded_img_count} 个封面图片")

    # 4. 保存新文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"\n🎉 打包完成！已生成全新的单网页文件 (包含所有音效、图片和封面):")
    print(f"👉 {output_path}")
    print("您可以直接将该 HTML 文件发送到任何设备直接打开玩耍！")

if __name__ == "__main__":
    embed_assets()
