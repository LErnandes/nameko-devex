import logging

from nameko.events import event_handler
from nameko.rpc import rpc

from products import dependencies
from products.schemas import Product


logger = logging.getLogger(__name__)


class ProductsService:

    name = 'products'

    storage = dependencies.Storage()

    @rpc
    def get(self, product_id):
        logger.debug(f'Get product by id - {product_id}')
        product = self.storage.get(product_id)
        return Product().dump(product).data

    @rpc
    def list(self):
        logger.debug('Get all products')
        products = self.storage.list()
        return Product(many=True).dump(products).data

    @rpc
    def create(self, product):
        logger.debug(f'Create product - {product}')
        product = Product(strict=True).load(product).data
        self.storage.create(product)

    @rpc
    def delete(self, product_id):
        logger.debug(f'Delete product by id - {product_id}')
        product = self.storage.delete(product_id)
        return Product().dump(product).data

    @event_handler('orders', 'order_created')
    def handle_order_created(self, payload):
        for product in payload['order']['order_details']:
            self.storage.decrement_stock(
                product['product_id'], product['quantity'])
