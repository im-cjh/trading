"""최적화된 파라미터 적용 스크립트"""
import sys
import json
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def load_optimized_params(optimization_dir: str = None) -> dict:
    """
    최적화 결과에서 최적 파라미터 로드
    
    Args:
        optimization_dir: 최적화 결과 디렉토리
        
    Returns:
        전략별 최적 파라미터 딕셔너리
    """
    if optimization_dir is None:
        optimization_dir = project_root / "data" / "optimization_results"
    else:
        optimization_dir = Path(optimization_dir)
    
    summary_file = optimization_dir / "optimization_summary.json"
    
    if not summary_file.exists():
        logger.error(f"Optimization summary not found: {summary_file}")
        return {}
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    
    # 각 전략별로 평균 성과가 가장 좋은 파라미터 선택
    best_params = {}
    
    for strategy_name, stock_results in summary.items():
        if not stock_results:
            continue
        
        # 모든 종목의 평균 수익률 계산
        best_stock = None
        best_score = -float('inf')
        
        for stock_code, result in stock_results.items():
            # 복합 점수 계산 (수익률 + 샤프비율 + 승률)
            score = (
                result['total_return'] * 0.4 +
                result['sharpe_ratio'] * 10 * 0.3 +
                result['win_rate'] * 0.3
            )
            
            if score > best_score:
                best_score = score
                best_stock = stock_code
        
        if best_stock:
            best_params[strategy_name] = stock_results[best_stock]['best_params']
            logger.info(f"{strategy_name}: Using params from {best_stock} (score: {best_score:.2f})")
    
    return best_params


def save_config(params: dict, config_path: str = None):
    """
    최적 파라미터를 설정 파일로 저장
    
    Args:
        params: 전략별 파라미터
        config_path: 저장 경로
    """
    if config_path is None:
        config_path = project_root / "config" / "optimized_params.json"
    else:
        config_path = Path(config_path)
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(params, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Optimized parameters saved to: {config_path}")


def apply_optimized_params():
    """최적화된 파라미터를 로드하고 설정 파일에 저장"""
    logger.info("Loading optimized parameters...")
    
    params = load_optimized_params()
    
    if not params:
        logger.error("No optimized parameters found!")
        return
    
    logger.info(f"Found optimized parameters for {len(params)} strategies")
    
    # 파라미터 출력
    print("\n" + "=" * 80)
    print("OPTIMIZED PARAMETERS")
    print("=" * 80)
    
    for strategy_name, strategy_params in params.items():
        print(f"\n{strategy_name}:")
        for param_name, param_value in strategy_params.items():
            print(f"  {param_name}: {param_value}")
    
    # 설정 파일에 저장
    save_config(params)
    
    print("\n" + "=" * 80)
    print("✅ Optimized parameters have been applied!")
    print("=" * 80)


if __name__ == "__main__":
    apply_optimized_params()
