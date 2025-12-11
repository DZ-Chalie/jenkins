from etl_integrated import parse_encyclopedia_price

# Test cases
test_cases = [
    "￦15,000 (가격은 판매처 별로 상이할 수 있습니다.)",
    "200ml ￦22,000, 500ml ￦49,000 (가격은 판매처 별로 상이할 수 있습니다)",
    "360ml ￦3,604 (가격은 판매처 별로 상이할 수 있습니다)",
    "￦1,980 (가격은 판매처 별로 상이할 수 있습니다.)",
    "750ml, 6%, ￦12,000(가격은 판매처 별로 상이할 수 있습니다.)",
]

print("=" * 60)
print("🧪 Price Parsing Tests")
print("=" * 60)

for price_str in test_cases:
    result = parse_encyclopedia_price(price_str)
    print(f"\nInput: {price_str[:60]}...")
    print(f"Output: ₩{result:,}")
