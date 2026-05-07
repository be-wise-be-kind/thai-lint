"""
Purpose: True positive code samples for Law of Demeter violation detection

Scope: Python code patterns that ARE genuine LoD violations

Overview: Contains inline Python code strings representing real Law of Demeter violations
    where an object reaches through intermediate objects to access deeply nested state.
    These samples should all be flagged by the linter. Derived from patterns observed in
    real-world codebases during prototype testing across 23 repos.

Dependencies: None (pure string constants)

Exports: String constants for true-positive test cases

Interfaces: Import constants by name

Implementation: Each constant is a complete Python code snippet parseable by ast.parse()
"""

# -- Reaching through objects to access nested state --

REACH_THROUGH_NESTED_OBJECT = """
def process_order(order):
    name = order.customer.address.city
"""

REACH_THROUGH_METHOD_RESULT = """
def get_info(service):
    data = service.get_client().fetch_data().parse()
"""

MULTIPLE_VIOLATIONS_IN_FUNCTION = """
def complex_handler(request):
    user_city = request.user.profile.address.city
    manager_name = request.department.manager.full_name
"""

CHAIN_WITH_MIXED_ATTR_AND_CALLS = """
def handle_event(event):
    result = event.get_source().get_handler().process()
"""

DEEP_ATTRIBUTE_ONLY_CHAIN = """
def render_template(ctx):
    title = ctx.page.header.title.text
"""

VIOLATION_IN_ASSIGNMENT = """
def save_record(db):
    table = db.engine.connection.cursor
"""

VIOLATION_IN_CONDITIONAL = """
def check_status(app):
    if app.server.connection.is_active:
        pass
"""

VIOLATION_IN_RETURN = """
def get_name(company):
    return company.department.head.name
"""

VIOLATION_IN_CALL_ARGUMENT = """
def log_info(system):
    print(system.network.adapter.mac_address)
"""

VIOLATION_IN_LOOP = """
def process_items(registry):
    for item in registry.store.shelf.items:
        pass
"""

VIOLATION_WITH_METHOD_CALL_MID_CHAIN = """
def transform(pipeline):
    output = pipeline.stage.get_transformer().run()
"""

VIOLATION_CLASS_METHOD = """
class Handler:
    def handle(self, ctx):
        name = ctx.request.user.profile.display_name
"""
