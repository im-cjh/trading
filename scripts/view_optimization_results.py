"""전략 성과 비교 및 시각화 대시보드"""
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

# 한글 폰트 설정 (Windows)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def load_optimization_results(results_dir: str = None) -> dict:
    """최적화 결과 로드"""
    if results_dir is None:
        results_dir = project_root / "data" / "optimization_results"
    else:
        results_dir = Path(results_dir)
    
    summary_file = results_dir / "optimization_summary.json"
    
    if not summary_file.exists():
        logger.error(f"Results not found: {summary_file}")
        return {}
    
    with open(summary_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_performance_comparison(results: dict, save_path: str = None):
    """전략별 성과 비교 차트 생성"""
    
    # 데이터 준비
    strategies = []
    returns = []
    win_rates = []
    sharpe_ratios = []
    max_drawdowns = []
    
    for strategy_name, stock_results in results.items():
        if not stock_results:
            continue
        
        # 모든 종목의 평균 계산
        avg_return = sum(r['total_return'] for r in stock_results.values()) / len(stock_results)
        avg_win_rate = sum(r['win_rate'] for r in stock_results.values()) / len(stock_results)
        avg_sharpe = sum(r['sharpe_ratio'] for r in stock_results.values()) / len(stock_results)
        avg_mdd = sum(r['max_drawdown'] for r in stock_results.values()) / len(stock_results)
        
        strategies.append(strategy_name.replace('Strategy', ''))
        returns.append(avg_return)
        win_rates.append(avg_win_rate)
        sharpe_ratios.append(avg_sharpe)
        max_drawdowns.append(avg_mdd)
    
    # 4개의 서브플롯 생성
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('전략 성과 비교 대시보드', fontsize=20, fontweight='bold')
    
    # 1. 총 수익률
    ax1 = axes[0, 0]
    colors = ['green' if r > 0 else 'red' for r in returns]
    ax1.barh(strategies, returns, color=colors, alpha=0.7)
    ax1.set_xlabel('수익률 (%)', fontsize=12)
    ax1.set_title('총 수익률', fontsize=14, fontweight='bold')
    ax1.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
    ax1.grid(axis='x', alpha=0.3)
    
    # 값 표시
    for i, v in enumerate(returns):
        ax1.text(v, i, f' {v:.2f}%', va='center', fontsize=10)
    
    # 2. 승률
    ax2 = axes[0, 1]
    ax2.barh(strategies, win_rates, color='skyblue', alpha=0.7)
    ax2.set_xlabel('승률 (%)', fontsize=12)
    ax2.set_title('승률', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 100)
    ax2.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(win_rates):
        ax2.text(v, i, f' {v:.1f}%', va='center', fontsize=10)
    
    # 3. 샤프 비율
    ax3 = axes[1, 0]
    colors_sharpe = ['green' if s > 0 else 'red' for s in sharpe_ratios]
    ax3.barh(strategies, sharpe_ratios, color=colors_sharpe, alpha=0.7)
    ax3.set_xlabel('샤프 비율', fontsize=12)
    ax3.set_title('샤프 비율 (위험 대비 수익)', fontsize=14, fontweight='bold')
    ax3.axvline(x=0, color='black', linestyle='--', linewidth=0.8)
    ax3.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(sharpe_ratios):
        ax3.text(v, i, f' {v:.2f}', va='center', fontsize=10)
    
    # 4. 최대 낙폭 (MDD)
    ax4 = axes[1, 1]
    ax4.barh(strategies, max_drawdowns, color='orange', alpha=0.7)
    ax4.set_xlabel('최대 낙폭 (%)', fontsize=12)
    ax4.set_title('최대 낙폭 (MDD)', fontsize=14, fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(max_drawdowns):
        ax4.text(v, i, f' {v:.2f}%', va='center', fontsize=10)
    
    plt.tight_layout()
    
    # 저장
    if save_path:
        save_file = Path(save_path) / f"performance_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        save_file.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_file, dpi=150, bbox_inches='tight')
        logger.info(f"Chart saved to: {save_file}")
    
    plt.show()


def create_detailed_table(results: dict):
    """상세 성과 테이블 출력"""
    
    print("\n" + "=" * 120)
    print("전략별 상세 성과 분석")
    print("=" * 120)
    
    for strategy_name, stock_results in results.items():
        print(f"\n📊 {strategy_name}")
        print("-" * 120)
        
        # 테이블 데이터 준비
        data = []
        for stock_code, result in stock_results.items():
            data.append({
                '종목코드': stock_code,
                '수익률(%)': f"{result['total_return']:.2f}",
                '승률(%)': f"{result['win_rate']:.2f}",
                '샤프비율': f"{result['sharpe_ratio']:.2f}",
                'MDD(%)': f"{result['max_drawdown']:.2f}",
                '최적파라미터': str(result['best_params'])
            })
        
        df = pd.DataFrame(data)
        print(df.to_string(index=False))
        
        # 평균 계산
        avg_return = sum(r['total_return'] for r in stock_results.values()) / len(stock_results)
        avg_win_rate = sum(r['win_rate'] for r in stock_results.values()) / len(stock_results)
        avg_sharpe = sum(r['sharpe_ratio'] for r in stock_results.values()) / len(stock_results)
        
        print(f"\n평균 - 수익률: {avg_return:.2f}%, 승률: {avg_win_rate:.2f}%, 샤프: {avg_sharpe:.2f}")
    
    print("\n" + "=" * 120)


def create_ranking(results: dict):
    """전략 종합 순위"""
    
    rankings = []
    
    for strategy_name, stock_results in results.items():
        if not stock_results:
            continue
        
        # 복합 점수 계산
        avg_return = sum(r['total_return'] for r in stock_results.values()) / len(stock_results)
        avg_win_rate = sum(r['win_rate'] for r in stock_results.values()) / len(stock_results)
        avg_sharpe = sum(r['sharpe_ratio'] for r in stock_results.values()) / len(stock_results)
        avg_mdd = sum(r['max_drawdown'] for r in stock_results.values()) / len(stock_results)
        
        # 종합 점수 (수익률 40% + 샤프비율 30% + 승률 30%)
        composite_score = (
            avg_return * 0.4 +
            avg_sharpe * 10 * 0.3 +
            avg_win_rate * 0.3
        )
        
        rankings.append({
            '전략': strategy_name.replace('Strategy', ''),
            '종합점수': composite_score,
            '수익률(%)': avg_return,
            '승률(%)': avg_win_rate,
            '샤프비율': avg_sharpe,
            'MDD(%)': avg_mdd
        })
    
    # 점수 순으로 정렬
    rankings.sort(key=lambda x: x['종합점수'], reverse=True)
    
    print("\n" + "=" * 100)
    print("🏆 전략 종합 순위")
    print("=" * 100)
    
    df = pd.DataFrame(rankings)
    df.index = range(1, len(df) + 1)
    df.index.name = '순위'
    
    # 포맷팅
    df['종합점수'] = df['종합점수'].apply(lambda x: f"{x:.2f}")
    df['수익률(%)'] = df['수익률(%)'].apply(lambda x: f"{x:.2f}")
    df['승률(%)'] = df['승률(%)'].apply(lambda x: f"{x:.2f}")
    df['샤프비율'] = df['샤프비율'].apply(lambda x: f"{x:.2f}")
    df['MDD(%)'] = df['MDD(%)'].apply(lambda x: f"{x:.2f}")
    
    print(df.to_string())
    print("=" * 100)


def main():
    """메인 대시보드 실행"""
    
    logger.info("Loading optimization results...")
    results = load_optimization_results()
    
    if not results:
        logger.error("No results to display!")
        return
    
    # 1. 상세 테이블
    create_detailed_table(results)
    
    # 2. 종합 순위
    create_ranking(results)
    
    # 3. 시각화 차트
    logger.info("Creating performance charts...")
    chart_save_path = project_root / "data" / "reports"
    create_performance_comparison(results, save_path=str(chart_save_path))
    
    logger.info("Dashboard complete!")


if __name__ == "__main__":
    main()
