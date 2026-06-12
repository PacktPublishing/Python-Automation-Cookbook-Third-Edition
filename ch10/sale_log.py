import parse
from decimal import Decimal
import pendulum


class SaleLog(object):

    def __init__(self, timestamp, product_id, price, name, discount,
                 shop=None, code=None):
        self.timestamp = timestamp
        self.product_id = product_id
        self.price = price
        self.name = name
        self.discount = discount
        self.shop = shop
        self.code = code

    def __repr__(self):
        return '<SaleLog ({}, {}, {})>'.format(self.timestamp,
                                               self.product_id,
                                               self.price)

    @classmethod
    def row_header(cls):
        HEADER = ('Timestamp', 'Shop', 'Product Id', 'Name', 'Price',
                  'Discount', 'Code')
        return HEADER

    def row(self):
        return (self.timestamp.isoformat(), self.shop,
                self.product_id, self.name, self.price,
                '{}%'.format(self.discount), self.code)

    @classmethod
    def from_row(cls, row):
        timestamp_str, shop, product_id, name, raw_price, discount_str, code = row
        timestamp = pendulum.parse(timestamp_str)
        discount = parse.parse('{:d}%', discount_str)[0]
        # Round to remove possible rounding errors in Excel
        price = round(Decimal(raw_price), 2)
        if code == '-':
            # In the spreadsheet, a dash is an empty code
            code = None

        return cls(timestamp=timestamp, product_id=product_id,
                   price=price, name=name, discount=discount,
                   shop=shop, code=code)

    @classmethod
    def parse(cls, shop, text_log):
        '''
        Parse from a text log with the format
        [<Timestamp>] - SALE - PRODUCT: <product id> - PRICE: $<price> - NAME: <name> - DISCOUNT: <discount>% - CODE: <code>
        to a SaleLog object
        '''
        def price(string):
            return Decimal(string)

        def isodate(string):
            return pendulum.parse(string)

        FORMAT = ('[{timestamp:isodate}] - SALE - PRODUCT: {product:d} '
                  '- PRICE: ${price:price} - NAME: {name:D} '
                  '- DISCOUNT: {discount:d}% '
                  '- CODE: {code:S}')

        # Remove trail new lines
        text_log = text_log.split('\n')[0]

        formats = {'price': price, 'isodate': isodate}
        result = parse.parse(FORMAT, text_log, formats)

        return cls(timestamp=result['timestamp'],
                   product_id=result['product'],
                   price=result['price'],
                   name=result['name'],
                   discount=result['discount'],
                   code=result['code'],
                   shop=shop)
