from . import orders, order_details, menu, resources, dashboard, reviews, promotions, analytics


def load_routes(app):
    app.include_router(orders.router)
    app.include_router(order_details.router)
    app.include_router(menu.router)
    app.include_router(resources.router)
    app.include_router(dashboard.router)
    app.include_router(reviews.router)
    app.include_router(promotions.router)
    app.include_router(analytics.router)
