"""
Purpose: TypeScript code sample fixtures for Law of Demeter tests

Scope: TypeScript code patterns for true-positive and false-positive LoD testing

Overview: Contains inline TypeScript code strings representing both genuine LoD violations
    and legitimate chain patterns (fluent APIs, module-qualified access, optional chaining).
    Used to test tree-sitter-based TypeScript analyzer. Covers React, Express, lodash, zod,
    and general TypeScript patterns.

Dependencies: None (pure string constants)

Exports: String constants for TypeScript test cases

Interfaces: Import constants by name

Implementation: Each constant is a complete TypeScript code snippet parseable by tree-sitter
"""

# =============================================================================
# TRUE POSITIVES - genuine LoD violations in TypeScript
# =============================================================================

TS_REACH_THROUGH_OBJECT = """
function processOrder(order: Order) {
    const city = order.customer.address.city;
}
"""

TS_METHOD_CHAIN_VIOLATION = """
function getData(service: Service) {
    return service.getClient().fetchData().parse();
}
"""

TS_DEEP_PROPERTY_ACCESS = """
function renderTitle(ctx: Context) {
    return ctx.page.header.title.text;
}
"""

# =============================================================================
# FALSE POSITIVES - should be filtered
# =============================================================================

# Module-qualified access
TS_MODULE_ACCESS = """
import express from 'express';
const app = express.Router().use(middleware).get('/');
"""

# Fluent API / builder
TS_FLUENT_BUILDER = """
function buildQuery(db: Database) {
    return db.select('*').where('active', true).orderBy('name').limit(10);
}
"""

# Optional chaining (should be allowed by default)
TS_OPTIONAL_CHAIN = """
function getCity(user?: User) {
    return user?.address?.city?.name;
}
"""

# String method chaining
TS_STRING_CHAIN = """
function clean(text: string) {
    return text.trim().toLowerCase().replace(/-/g, '_');
}
"""

# React pattern - safe prefix (this.)
TS_REACT_THIS = """
class MyComponent extends React.Component {
    render() {
        return this.props.config.theme.color;
    }
}
"""

# Promise chaining (fluent)
TS_PROMISE_CHAIN = """
function fetchData(url: string) {
    return fetch(url).then(r => r.json()).then(data => data.result);
}
"""

# Array method pipeline
TS_ARRAY_PIPELINE = """
function transform(items: Item[]) {
    return items.filter(x => x.active).map(x => x.name).join(', ');
}
"""
