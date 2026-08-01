# pinpai.ai.in DNS配置指引
# 
# 需要老板登录 Dynadot 后添加以下记录：
#
# 目标：pinpai.ai.in → GitHub Pages
# GitHub Pages IP: (根据域名解析)
#
# 推荐配置：
# 类型: A      主机: @    值: 185.199.108.153   (GitHub Pages)
# 类型: A      主机: @    值: 185.199.109.153
# 类型: A      主机: @    值: 185.199.110.153
# 类型: A      主机: @    值: 185.199.111.153
# 类型: CNAME  主机: www  值: wqf2956041-star.github.io.
#
# 或者直接用CNAME（如果Dynadot支持根域名CNAME）：
# 类型: CNAME  主机: @    值: wqf2956041-star.github.io.
#
# 配置好后，GitHub Pages会自动签发HTTPS证书
# https://pinpai.ai.in 即可访问
