"""베이지안 최적화 엔진"""
import numpy as np
from typing import Dict, List, Any, Callable, Tuple
from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
import json
from pathlib import Path
from ..logger import get_logger
from .backtester import Backtester

logger = get_logger(__name__)


class BayesianOptimizer:
    """
    베이지안 최적화를 사용한 전략 파라미터 튜닝
    """
    
    def __init__(self, backtester: Backtester = None):
        self.backtester = backtester or Backtester()
        self.optimization_history = []
        
    def optimize_strategy(
        self,
        strategy_class,
        stock_code: str,
        param_bounds: Dict[str, Tuple[float, float]],
        n_iterations: int = 50,
        init_points: int = 10,
        objective: str = 'sharpe_ratio',  # 'total_return', 'sharpe_ratio', 'win_rate'
        save_path: str = None
    ) -> Dict[str, Any]:
        """
        전략 파라미터 최적화
        
        Args:
            strategy_class: 최적화할 전략 클래스
            stock_code: 종목 코드
            param_bounds: 파라미터 범위 {'param_name': (min, max), ...}
            n_iterations: 최적화 반복 횟수
            init_points: 초기 랜덤 탐색 포인트 수
            objective: 최적화 목표 ('total_return', 'sharpe_ratio', 'win_rate')
            save_path: 결과 저장 경로
            
        Returns:
            최적화 결과 딕셔너리
        """
        logger.info(f"Starting Bayesian Optimization for {strategy_class.__name__} on {stock_code}")
        logger.info(f"Parameter bounds: {param_bounds}")
        logger.info(f"Iterations: {n_iterations}, Init points: {init_points}, Objective: {objective}")
        
        # 목적 함수 정의
        def objective_function(**params):
            """
            베이지안 최적화가 최대화할 목적 함수
            """
            # 정수형 파라미터 처리 (예: RSI period는 정수여야 함)
            processed_params = {}
            for key, value in params.items():
                if 'period' in key or 'window' in key:
                    processed_params[key] = int(round(value))
                else:
                    processed_params[key] = value
            
            # 전략 인스턴스 생성
            strategy = strategy_class(config=processed_params)
            
            # 백테스트 실행
            result = self.backtester.run_backtest(
                strategy=strategy,
                stock_code=stock_code,
                days=90  # 3개월 데이터로 테스트
            )
            
            # 목적 함수 값 계산
            if objective == 'total_return':
                score = result['total_return']
            elif objective == 'sharpe_ratio':
                score = result['sharpe_ratio']
            elif objective == 'win_rate':
                score = result['win_rate']
            else:
                # 복합 점수: 수익률 + 샤프비율 + 승률
                score = (
                    result['total_return'] * 0.4 +
                    result['sharpe_ratio'] * 10 * 0.3 +  # 스케일 조정
                    result['win_rate'] * 0.3
                )
            
            # 거래 횟수가 너무 적으면 패널티
            if result['total_trades'] < 5:
                score *= 0.5
            
            # MDD가 너무 크면 패널티
            if result['max_drawdown'] < -30:  # -30% 이상 손실
                score *= 0.7
            
            logger.info(f"Params: {processed_params} -> Score: {score:.4f} "
                       f"(Return: {result['total_return']:.2f}%, "
                       f"Sharpe: {result['sharpe_ratio']:.2f}, "
                       f"Win Rate: {result['win_rate']:.2f}%)")
            
            return score
        
        # 베이지안 최적화 실행
        optimizer = BayesianOptimization(
            f=objective_function,
            pbounds=param_bounds,
            random_state=42,
            verbose=2
        )
        
        # 로깅 설정 (선택사항)
        if save_path:
            log_path = Path(save_path) / f"{strategy_class.__name__}_{stock_code}_optimization.json"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            logger_obj = JSONLogger(path=str(log_path))
            optimizer.subscribe(Events.OPTIMIZATION_STEP, logger_obj)
        
        # 최적화 실행
        optimizer.maximize(
            init_points=init_points,
            n_iter=n_iterations
        )
        
        # 최적 파라미터 추출
        best_params = optimizer.max['params']
        
        # 정수형 파라미터 변환
        for key in best_params.keys():
            if 'period' in key or 'window' in key:
                best_params[key] = int(round(best_params[key]))
        
        # 최적 파라미터로 최종 백테스트
        best_strategy = strategy_class(config=best_params)
        final_result = self.backtester.run_backtest(
            strategy=best_strategy,
            stock_code=stock_code,
            days=90
        )
        
        optimization_result = {
            'strategy_name': strategy_class.__name__,
            'stock_code': stock_code,
            'best_params': best_params,
            'best_score': optimizer.max['target'],
            'backtest_result': final_result,
            'optimization_history': [
                {
                    'params': res['params'],
                    'score': res['target']
                }
                for res in optimizer.res
            ]
        }
        
        logger.info(f"Optimization completed!")
        logger.info(f"Best parameters: {best_params}")
        logger.info(f"Best score: {optimizer.max['target']:.4f}")
        logger.info(f"Final backtest - Return: {final_result['total_return']:.2f}%, "
                   f"Win Rate: {final_result['win_rate']:.2f}%, "
                   f"Sharpe: {final_result['sharpe_ratio']:.2f}")
        
        # 결과 저장
        if save_path:
            result_path = Path(save_path) / f"{strategy_class.__name__}_{stock_code}_result.json"
            with open(result_path, 'w', encoding='utf-8') as f:
                # datetime 객체를 문자열로 변환
                serializable_result = self._make_serializable(optimization_result)
                json.dump(serializable_result, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {result_path}")
        
        return optimization_result
    
    def optimize_multiple_strategies(
        self,
        strategy_configs: List[Dict[str, Any]],
        stock_codes: List[str],
        n_iterations: int = 50,
        save_path: str = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        여러 전략과 종목에 대해 일괄 최적화
        
        Args:
            strategy_configs: [{'class': StrategyClass, 'param_bounds': {...}}, ...]
            stock_codes: 종목 코드 리스트
            n_iterations: 각 최적화당 반복 횟수
            save_path: 결과 저장 경로
            
        Returns:
            전략별, 종목별 최적화 결과
        """
        results = {}
        
        for config in strategy_configs:
            strategy_class = config['class']
            param_bounds = config['param_bounds']
            strategy_name = strategy_class.__name__
            
            results[strategy_name] = {}
            
            for stock_code in stock_codes:
                logger.info(f"\n{'='*60}")
                logger.info(f"Optimizing {strategy_name} for {stock_code}")
                logger.info(f"{'='*60}\n")
                
                try:
                    result = self.optimize_strategy(
                        strategy_class=strategy_class,
                        stock_code=stock_code,
                        param_bounds=param_bounds,
                        n_iterations=n_iterations,
                        save_path=save_path
                    )
                    results[strategy_name][stock_code] = result
                    
                except Exception as e:
                    logger.error(f"Optimization failed for {strategy_name} on {stock_code}: {e}")
                    results[strategy_name][stock_code] = None
        
        return results
    
    def _make_serializable(self, obj):
        """JSON 직렬화 가능하도록 변환"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'isoformat'):  # datetime 객체
            return obj.isoformat()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        else:
            return obj
