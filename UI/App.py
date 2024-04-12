import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],use_pages=True) #user pages = true allows it to be multipage IMPORTANT!
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("View Other Clients", href="/ClientList")),
        dbc.NavItem(dbc.NavLink("Sync Projects", href="/syncMenue")),
        dbc.NavItem(dbc.NavLink("Manage Projects", href="/manageProjects")),
        dbc.NavItem(dbc.NavLink("Home", href="/")), #temporary replace with image


    ],
    brand="Background changer",
    brand_href="#",
    color="primary",
    dark=True,
    className="fixed-top",
)
hiddenStore = dcc.Store(id='passedData')
app.layout = html.Div([
    dcc.Location(id='location'),
    dcc.Store(id='selected-project-store', data=None,storage_type = 'local'),
    dcc.Store(id='eventStore', data=None,storage_type = 'local'), # local makes it persistent
    navbar,
    dash.page_container,
])

if __name__ == '__main__':
    app.run(debug=True)