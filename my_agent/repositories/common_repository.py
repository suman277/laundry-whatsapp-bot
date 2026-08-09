from ..models.user_model import User
from ..models.orders_model import OrderItem, Order, OrderView, DashboardView
from ..repositories.generic_repository import GenericRepository

UserRepository = GenericRepository(User)
OrderItemRepository = GenericRepository(OrderItem)
OrderRepository = GenericRepository(Order)
OrderViewRepository = GenericRepository(OrderView)
DashboardViewRepository = GenericRepository(DashboardView)