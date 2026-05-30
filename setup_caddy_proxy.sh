#!/bin/bash
# 在宿主机（新加坡虚拟机）上执行
# 用途：让 pinpai.ai.in 通过 Caddy 反向代理到 GitHub Pages

# 检查是否已有 pinpai.ai.in 配置
if sudo grep -q "pinpai.ai.in" /etc/caddy/Caddyfile 2>/dev/null; then
    echo "pinpai.ai.in 已存在 Caddyfile 中，请手动检查"
    sudo cat /etc/caddy/Caddyfile | grep -A5 "pinpai.ai.in"
    exit 1
fi

# 追加到 Caddyfile
sudo tee -a /etc/caddy/Caddyfile << 'EOF'

pinpai.ai.in {
    # 反向代理到 GitHub Pages
    reverse_proxy https://wqf2956041-star.github.io {
        header_up Host wqf2956041-star.github.io
        header_up X-Forwarded-Host pinpai.ai.in
    }

    # 国内用户缓存优化
    header Cache-Control "public, max-age=3600"
    encode gzip

    # 日志
    log {
        output file /var/log/caddy/pinpai-ai-in.log
    }
}
EOF

echo "✅ 配置已写入 /etc/caddy/Caddyfile"

# 重新加载 Caddy
sudo caddy reload --config /etc/caddy/Caddyfile

echo "✅ Caddy 已重新加载"
