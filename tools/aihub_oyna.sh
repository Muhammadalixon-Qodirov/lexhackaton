#!/bin/bash
# AIHUB serveridagi brauzer oynasini VNC ekranida oldinga chiqarish.
# Ishlatish: ./tools/aihub_oyna.sh gemini | chatgpt | claude | google | royxat
# (server paroli so'raladi)
Q="${1:-royxat}"
ssh root@185.174.254.135 "sudo -u einvestment env DISPLAY=:99 bash -c '
if [ \"$Q\" = royxat ]; then for w in \$(xdotool search --onlyvisible --name . 2>/dev/null); do echo \"\$w | \$(xdotool getwindowname \$w)\"; done; exit; fi
W=\$(xdotool search --onlyvisible --name \"$Q\" 2>/dev/null | head -1)
[ -z \"\$W\" ] && { echo \"$Q oynasi topilmadi\"; exit 1; }
xdotool windowraise \$W; xdotool windowfocus \$W 2>/dev/null; echo \"oldinga chiqarildi: \$(xdotool getwindowname \$W)\"
'"
