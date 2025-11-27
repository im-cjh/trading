"""설정 모드 전환 스크립트"""
import sys
import yaml
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def switch_mode(new_mode: str):
    """거래 모드 전환
    
    Args:
        new_mode: 'mock' 또는 'real'
    """
    if new_mode not in ['mock', 'real']:
        print(f"❌ Invalid mode: {new_mode}")
        print("   Valid modes: 'mock' or 'real'")
        return False
    
    config_path = project_root / "config" / "config.yaml"
    
    # config.yaml 로드
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    old_mode = config.get('trading_mode', 'unknown')
    
    # 모드 변경
    config['trading_mode'] = new_mode
    
    # 저장
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"✓ Trading mode switched: {old_mode} → {new_mode}")
    
    if new_mode == 'real':
        print("\n⚠️  WARNING: Real trading mode activated!")
        print("   Make sure you have proper API credentials configured.")
        print("   All orders will be executed with real money!")
    
    return True


def show_current_mode():
    """현재 모드 표시"""
    config_path = project_root / "config" / "config.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    mode = config.get('trading_mode', 'unknown')
    print(f"Current trading mode: {mode}")
    
    return mode


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Trading Mode Switcher')
    parser.add_argument(
        'mode',
        nargs='?',
        choices=['mock', 'real', 'show'],
        help='Trading mode to switch to (or "show" to display current mode)'
    )
    
    args = parser.parse_args()
    
    if not args.mode or args.mode == 'show':
        show_current_mode()
    else:
        switch_mode(args.mode)


if __name__ == "__main__":
    main()
