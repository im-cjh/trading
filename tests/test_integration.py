"""간단한 통합 테스트"""
import pytest
import asyncio
from src.execution import MockExecutor, OrderExecutor
from src.api.kis_models import OrderRequest


@pytest.mark.asyncio
async def test_mock_executor_buy_sell():
    """모의투자 매수/매도 테스트"""
    executor = MockExecutor(initial_cash=10000000)
    
    # 초기 잔고 확인
    balance = executor.get_account_balance()
    assert balance.cash == 10000000
    assert balance.stock_value == 0
    
    # 현재가 설정
    executor.update_price("005930", 70000)
    
    # 매수 주문
    buy_order = OrderRequest(
        stock_code="005930",
        order_type="buy",
        price=70000,
        quantity=10
    )
    
    response = executor.place_order(buy_order)
    assert response.status == "filled"
    
    # 잔고 확인
    balance = executor.get_account_balance()
    assert balance.cash == 10000000 - 700000  # 70,000 * 10
    assert len(executor.get_positions()) == 1
    
    # 매도 주문
    sell_order = OrderRequest(
        stock_code="005930",
        order_type="sell",
        price=75000,
        quantity=10
    )
    
    response = executor.place_order(sell_order)
    assert response.status == "filled"
    
    # 잔고 확인
    balance = executor.get_account_balance()
    assert balance.cash == 10000000 - 700000 + 750000  # 매수 후 매도
    assert len(executor.get_positions()) == 0
    
    # 수익 확인
    assert balance.profit_loss == 50000  # 75,000 - 70,000 per share * 10


@pytest.mark.asyncio
async def test_order_validation():
    """주문 유효성 검사 테스트"""
    executor = OrderExecutor(mode='mock')
    
    # 잘못된 가격
    invalid_order = OrderRequest(
        stock_code="005930",
        order_type="buy",
        price=-1000,
        quantity=10
    )
    
    response = await executor.place_order(invalid_order)
    assert response.status == "rejected"
    
    # 잘못된 수량
    invalid_order = OrderRequest(
        stock_code="005930",
        order_type="buy",
        price=70000,
        quantity=0
    )
    
    response = await executor.place_order(invalid_order)
    assert response.status == "rejected"


def test_position_calculations():
    """포지션 계산 테스트"""
    executor = MockExecutor(initial_cash=10000000)
    executor.update_price("005930", 70000)
    
    # 첫 번째 매수
    order1 = OrderRequest(
        stock_code="005930",
        order_type="buy",
        price=70000,
        quantity=10
    )
    executor.place_order(order1)
    
    # 두 번째 매수 (다른 가격)
    order2 = OrderRequest(
        stock_code="005930",
        order_type="buy",
        price=72000,
        quantity=5
    )
    executor.place_order(order2)
    
    # 평균 단가 확인
    positions = executor.get_positions()
    assert len(positions) == 1
    
    pos = positions[0]
    assert pos.quantity == 15
    # 평균 단가: (70000*10 + 72000*5) / 15 = 70666.67
    expected_avg = int((70000 * 10 + 72000 * 5) / 15)
    assert pos.avg_price == expected_avg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
