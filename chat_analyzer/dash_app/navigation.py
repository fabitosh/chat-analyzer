from dash import html, page_registry
import dash_bootstrap_components as dbc


def create_navbar():
    navbar = dbc.NavbarSimple(
        children=
            [dbc.NavItem(dbc.NavLink(page['name'],
                                     href=page['relative_path'],
                                     target=page['relative_path'])) for page in page_registry.values()],
        brand='chat-analyzer',
        brand_href="/",
        sticky="top",
        # color="dark",
    )
    return navbar
