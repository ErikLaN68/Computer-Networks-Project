import dash
import dash_bootstrap_components as dbc
from dash import html,callback,Input, Output, State
import dash_ag_grid as dag

dash.register_page(__name__, path='/ClientList')

modal = html.Div(
    [
        dbc.Button("+ Create Project", color="primary", style={'display': 'inline-block'} , className="position-absolute top-0 end-0 m-3", id = "open", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Create Project")),
                dbc.ModalBody(
                    [
                        html.P("Project Name"),
                        dbc.Form(
                            dbc.Row(dbc.Col(html.Div(dbc.Input(type="Project Name", placeholder="Project Name", id = "projectName" )),width = 12),)
                        ),
                        html.Br(),
                        html.P("Project Location"),
                        dbc.Form(
                            dbc.Row(dbc.Col(html.Div(dbc.Input(type="Project Location", placeholder="Project Location", id = "projectLocation")),width = 12),)
                        ),
                        html.Br(),
                        html.P("Log Location"),
                        dbc.Form(
                            dbc.Row(dbc.Col(html.Div(dbc.Input(type="Log Directory", placeholder="Log Directory" , id = "logDirectory")),width = 12),)
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(html.P("Start Date")),
                                dbc.Col(html.P("End Date")),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Form(dbc.Row(dbc.Col(html.Div(dbc.Input(type="Start Date", placeholder="mm/dd/yyyy")))))),
                                dbc.Col(dbc.Form(dbc.Row(dbc.Col(html.Div(dbc.Input(type="End Date", placeholder="mm/dd/yyyy")))))),
                            ]
                        ),
                        html.Br(),
                        html.P("Initials"),
                        dbc.Form(
                            dbc.Row(dbc.Col(html.Div(dbc.Input(type="Initials", placeholder="III", id = "analystInitals")),width = 6),)
                        ),
                        
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Button("Cancel", size = "lg", color="secondary", id="close", className="ms-auto", n_clicks=0)),
                                dbc.Col(dbc.Button("Create Project", size = "lg", color="primary", id="createProject", className="ms-auto", href="/manageProjects",n_clicks=0)),
                            ]
                        ),
                    ],
                ),
                dbc.ModalFooter(
                    [
                        
                    ]
                ),
            ],
            id = "modal",
            is_open = False,
        ),
    ]
    
)

modal_2 = html.Div(
    [
        html.Div(
            [
                dbc.Button("Ingest Logs", color="primary",id = "open modal_2"),
                dbc.Button("Delete Project", color="primary",href = "#"),
                dbc.Button("Open Project", color="primary",href = "#"),
            ],
            className="d-grid gap-2 d-md-flex justify-content-md-end position-absolute bottom-0 end-0 m-3",
        ), 
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Ingest Logs")),
                dbc.ModalBody(
                    [
                        html.P("Select a directory to ingest logs from."),
                        html.P("Log directory", style={"font-size": "20px",'display': 'inline-block'}),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Form(dbc.Row(dbc.Col(html.Div(dbc.Input(type="Log Directory", placeholder="ex. /Location/folder"))))), width = 9),
                                dbc.Col(dbc.Button("Browse", color="primary",id = "Browse")),
                            ]
                        ),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Button("Cancel", size = "lg", color="secondary", id="close modal_2", className="ms-auto", n_clicks=0)),
                                dbc.Col(dbc.Button("Ingest Logs", size = "lg", color="primary", id="create Project", className="ms-auto", n_clicks=0)),
                            ]
                        ),
                    ]
                ),
                dbc.ModalFooter(),
            ],
            id = "modal_2",
            is_open = False,
        ),
    ]
    
)

modal_3 = html.Div(
    [
        html.Div(
            [
                dbc.Button("Delete Project", color="primary",id = "open modal_3"),
                dbc.Button("Open Project", color="primary"),
            ],
            className="d-grid gap-2 d-md-flex justify-content-md-end position-absolute bottom-0 end-0 m-3",
        ), 
        dbc.Modal(
            [
                dbc.ModalHeader(),
                dbc.ModalBody(
                    [
                        html.P("Are you sure you want to delete Project D?", style={"font-size": "40px", "margin-left": "10px", 'display': 'inline-block'}),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(dbc.Button("Cancel", size = "lg", color="secondary", id="close modal_3", className="ms-auto", n_clicks=0)),
                                dbc.Col(dbc.Button("Delete", size = "lg", color="primary", id="delete Project", className="ms-auto", n_clicks=0)),
                            ]
                        ),
                    ]
                ),
                dbc.ModalFooter(),
            ],
            id = "modal_3",
            is_open = False,
        ),
    ]
    
)

modal_4 = html.Div(
    [
        html.Div(
            [
                dbc.Button("Open Project", color="primary",id = "open modal_4",href="/displayEvents"),
            ],
            className="d-grid gap-2 d-md-flex justify-content-md-end position-absolute bottom-0 end-0 m-3",
        ), 
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Open Project")),
                dbc.ModalBody("This is the content of the modal"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close modal_4", className="ms-auto", n_clicks=0)
                ),
            ],
            id = "modal_4",
            is_open = False,
        ),
    ]
    
)

def createTable():
    ClientList = ClientList = [
        {"Name": "Ricky", "ip": "172.0.0", "port": 30},
        {"Name": "Bobby", "ip": "172.0.0", "port": 25},
        # Add more rows as needed
    ]   
    columnDefs = [
        {"headerName": "Name", "field": "Name", "sortable": True},
        {"headerName": "ip", "field": "ip", "sortable": True},
        {"headerName": "port", "field": "port", "sortable": True},
        # More column definitions...
    ]
    return dag.AgGrid(
            id="row-selection-selected-rows",
            columnDefs=columnDefs,
            rowData=ClientList,
            columnSize="sizeToFit",
            defaultColDef={"filter": True},
            dashGridOptions={"rowSelection": "multiple", "animateRows": False},
            persistence=True,        
            persisted_props=["data"], 
        )



@callback(
    [Output('selected-project-store', 'data')],
    [Input("row-selection-selected-rows", "selectedRows")],
    [State('selected-project-store', 'data')]
)
def output_selected_rows(selected_rows,current_data):
    if selected_rows is None:
        return (current_data,)
    else:
        selectedProject = [f"{project['_id']}" for project in selected_rows]
        return (f"{'s' if len(selected_rows) > 1 else ''}{', '.join(selectedProject)}",)

def generateManageProjectCard():
   return html.Div(
    dbc.Card(
        
        dbc.Row(
            id="control-card",
            children=[
                dbc.Col(width=1), #gives the card nice margin
                dbc.Col([
                        dbc.Col([
                        html.Img(
                        src=dash.get_asset_url("fileImage.png"),
                        className="img-fluid rounded-start",
                        style={"width": "90px", "height": "90px","margin-right": 0, "margin-bottom" : "0%", "padding-top" : "0%"}, #inline alows for the html to stack on one line
                        ), 
                        html.P("Client List", style={"font-size": "40px","margin-left": 0,'display': 'inline-block' ,'padding-left': '20px'}),
                        ]),
                        modal,
                        modal_2,
                        modal_3,
                        modal_4,
                        html.Br(),
                        createTable(),


                        html.A(html.Button('Refresh Data'),href='/ClientList'),
                        
                        
                        html.P(id='placeholder')
                ]
                ),
                dbc.Col(width=1)
            ],
        
        ), style={"height": "42vw", "width": "90vw",},className="mx-auto"
        
       
    )
)

@callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks"),Input('createProject', 'n_clicks')],
    [
        State("modal", "is_open"),
        State('projectName', 'value'),
        State('analystInitals', 'value'),
        State('logDirectory', 'value'),
        ],
)
def toggle_modal(n1, n2, n3, is_open,projectName, analystInitals,logDirectory):
    if n1 or n2:
        #if n3:
           #projectManager.createProject(projectName,analystInitals,logDirectory)
        return not is_open

@callback(
    Output("modal_2", "is_open"),
    [Input("open modal_2", "n_clicks"), Input("close modal_2", "n_clicks")],
    [State("modal_2", "is_open")],
)
def toggle_modal_2(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output("modal_3", "is_open"),
    [Input("open modal_3", "n_clicks"), Input("close modal_3", "n_clicks")],
    [State("modal_3", "is_open")],
)
def toggle_modal_3(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@callback(
    Output("modal_4", "is_open"),
    [Input("open modal_4", "n_clicks"), Input("close modal_4", "n_clicks")],
    [State("modal_4", "is_open")],
)
def toggle_modal_4(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

def serveLayout():
    return html.Div([
        dbc.Container([
            html.Div(id ="dummyDivManageProject"),
        generateManageProjectCard(),
        ], fluid=True, style={"backgroundColor": "#D3D3D3", "margin": "auto", "height": "100vh", "display": "flex", "flexDirection": "column", "justifyContent": "center"}) 
    ])

layout = serveLayout

