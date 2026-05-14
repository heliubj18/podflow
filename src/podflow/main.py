import shutil
import sys

import uvicorn

from podflow.config import load_config


def _check_env():
    checks = []
    v = sys.version_info
    checks.append(("Python 3.10+", v >= (3, 10)))
    checks.append(("ffmpeg", shutil.which("ffmpeg") is not None))
    return checks


def cli():
    config = load_config()
    checks = _check_env()

    print("\n🎙️  PodFlow v0.1.0\n")
    print("📋 环境检测:")
    for name, ok in checks:
        icon = "✅" if ok else "❌"
        print(f"   {icon} {name}")

    print()
    print("💡 提示:")
    print("   • 在设置页配置 LLM 和 TTS 后端")
    print("   • TTS 默认使用 Edge-TTS (免费在线)")
    print()
    print(f"🚀 服务已启动: http://localhost:{config.server.port}\n")

    uvicorn.run(
        "podflow.app:app",
        host=config.server.host,
        port=config.server.port,
        reload=False,
        log_level="warning",
    )


if __name__ == "__main__":
    cli()
