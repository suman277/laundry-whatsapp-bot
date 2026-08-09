from enum import Enum


class StatusEnum(int, Enum):
    PENDING = 1                    # Customer placed the order
    CONFIRMED = 2                # Order accepted by EcoRinse
    PICKED_UP = 3               # Clothes collected from customer
    PROCESSING = 4             # Washing / Dry Cleaning / Ironing in progress
    READY_FOR_DELIVERY = 5  # Ready to be dispatched
    OUT_FOR_DELIVERY = 6  # Delivery partner is delivering
    DELIVERED = 7               # Successfully delivered
    CANCELLED = 8