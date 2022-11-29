# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output, ctx
import dash_bootstrap_components as dbc
import plotly.express as px
from skimage import io
from skimage.transform import rescale

import scipy.io
import numpy as np
import pandas as pd
import glob
import os

from rich.console import Console

from tkinter import filedialog
from tkinter import *

console = Console()
hololens_folder = "/hololens_camera-rgb-image_raw-compressed/"
camera1_folder = "/cam_1-color-image_raw/"
camera2_folder = "/cam_2-rgb-image_rect_color/"
mocap_start_time = 0
p1_mocap_id = 3
video_offset = 8

# Mocap label reference:
# ['Hammer' 'Right Elbow' 'Left Elbow' 'Right Shoulder' 'Left Shoulder'
#  'Right Wrist Pinky' 'Right Wrist Thumb' 'Right Pinky' 'Right Index'
#  'Right Thumb' 'Left Wrist Pinky' 'Left Wrist Thumb' 'Left Thumb'
#  'Left Index' 'Left Pinky' 'Knife Tip' 'Knife Stem']

colors = {
    'background': '#968f8f',
    'text': '#7FDBFF'
}


class DataProcessServer(object):
    def __init__(self):
        Tk().withdraw()
        self.parent_dir = filedialog.askdirectory()

        self.frame_idx = 0
        self.read_frames()
        self.load_mocap_mat()

        self.app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])
        self.app.layout = self.generate_layout()
        self.register_callbacks()

        self.hololens_hammer_point = 0
        self.camera1_hammer_point = 0
        self.camera2_hammer_point = 0
        self.mocap_hammer_point = 0

    def read_frames(self):
        """Read frame collection from path"""
        print(self.parent_dir + hololens_folder)
        self.hololens_frames = io.imread_collection(
            self.parent_dir + hololens_folder + "*.jpg")
        console.print(f'Read {len(self.hololens_frames)} hololens frames')
        self.cam1_frames = io.imread_collection(
            self.parent_dir + camera1_folder + "*.jpg")
        console.print(f'Read {len(self.cam1_frames)} camera1 frames')
        self.cam2_frames = io.imread_collection(
            self.parent_dir + camera2_folder + "*.jpg")
        console.print(f'Read {len(self.cam2_frames)} camera2 frames')

    def load_mocap_mat(self):
        # return the first found mat file
        mat_path = glob.glob(self.parent_dir+"/*.mat")[0]
        mocap_name = os.path.splitext(os.path.basename(mat_path))[0]
        self.entry_name = mocap_name
        self.p1_mat = scipy.io.loadmat(mat_path, simplify_cells=True)
        console.print(f"Read mocap data from {mat_path}")
        console.print("Mocap labels")
        console.print(self.p1_mat[mocap_name]
                      ['Trajectories']['Labeled']['Labels'])
        self.p1_label = (self.p1_mat[mocap_name]
                         ['Trajectories']['Labeled']['Labels'])
        console.print(self.p1_mat[mocap_name]
                      ['Trajectories']['Labeled']['Data'][p1_mocap_id, :, :].T.shape)
        self.p1_df = pd.DataFrame(self.p1_mat[mocap_name]['Trajectories']
                                  ['Labeled']['Data'][p1_mocap_id, 0:3, mocap_start_time:].T, columns=['x', 'y', 'z'])

    def update_text(self, n):
        return [html.Span('Test'+str(n))]

    def register_callbacks(self):
        self.app.callback(
            Output('hololens-graph', 'figure'),
            Output('cam1-graph', 'figure'),
            Output('cam2-graph', 'figure'),
            Input('slider-frame', 'value'),
            Input('btn-next', 'n_clicks'),
            Input('btn-prev', 'n_clicks')
            # Input('interval', 'n_intervals')
        )(self.update_frames)

        self.app.callback(
            Output('plot1-graph', 'figure'),
            Input('slider-frame', 'value')
        )(self.update_plots)

        self.app.callback(
            Output('sync-time', "value"),
            Input('hololens-hammer-frame', "value"),
            Input('camera1-hammer-frame', "value"),
            Input('camera2-hammer-frame', "value"),
            Input('mocap-hammer-frame', "value")
        )(self.sync_hammer)

    def generate_layout(self):
        """Generate and return app components layout"""
        return html.Div(
            [
                dbc.Row(
                    dbc.Col(html.H1("Fish Cutting Data Analysis", className="btn-primary"))),
                dbc.Row(dbc.Col(html.H2(self.entry_name,
                                        className="btn-primary"), width=2)),
                dbc.Row(dbc.Col(html.Br(id="sync-time"))),
                dbc.Row([
                        dbc.Col(html.Div([
                            html.H3("Hololens", className="btn-secondary"),
                            dcc.Graph(id='hololens-graph'),
                        ])),
                        dbc.Col(html.Div([
                            html.H3("Camera1", className="btn-secondary"),
                            dcc.Graph(id='cam1-graph'),
                        ])),
                        dbc.Col(html.Div([
                            html.H3("Camera2", className="btn-secondary"),
                            dcc.Graph(id='cam2-graph'),
                        ]))
                        ]),
                dbc.Row([
                        dbc.Col(html.H3("Hololens hammer point: ", className="btn-secondary"), width=2),
                        dbc.Col(dcc.Input(id="hololens-hammer-frame", type="number", value=0,
                                           debounce=True, placeholder="Hammer Frame"), width=2),
                        dbc.Col(html.H3("Camera1 hammer point: ", className="btn-secondary"), width=2),
                        dbc.Col(dcc.Input(id="camera1-hammer-frame", type="number", value=0,
                                           debounce=True, placeholder="Hammer Frame"), width=2),
                        dbc.Col(html.H3("Camera2 hammer point: ", className="btn-secondary"), width=2),
                        dbc.Col(dcc.Input(id="camera2-hammer-frame", type="number", value=0,
                                           debounce=True, placeholder="Hammer Frame"), width=2)]),
                dbc.Row([
                    dbc.Col([
                        html.H2(
                            f"Tracker {self.p1_label[p1_mocap_id]}", className="btn-warning"),
                        dcc.Graph(id='plot1-graph',
                                  figure=px.line(self.p1_df, labels={'index': 'time (10ms)', 'value': 'pos'}, range_x=[0, 3000]))
                    ], width=4),
                ]),

                dbc.Row([dbc.Col(html.H3("Mocap hammer point: ", className="btn-warning"), width=2),
                         dbc.Col(dcc.Input(id="mocap-hammer-frame", type="number", value=0,
                                           debounce=True, placeholder="Hammer Frame"), width=1)]),
                dbc.Row(dbc.Col(html.Br())),
                dbc.Row(dbc.Col(html.Br())),

                dbc.Row([
                    dbc.Col(html.Button('Next frame', id='btn-next',
                                        className='btn btn-primary', n_clicks=0), width=1),
                    dbc.Col(html.Button('Prev frame', id='btn-prev',
                                        className='btn btn-primary', n_clicks=0), width=1),
                    dbc.Col(
                        dcc.Slider(0, len(self.hololens_frames)-1, 1, value=0, marks=None,
                                   tooltip={"placement": "bottom",
                                            "always_visible": True},
                                   id='slider-frame',
                                   updatemode='drag',
                                   className='form-range')
                    )
                ]),
                # dcc.Interval(id="interval", interval=150)
            ]
        )

    def update_frames(self, slider_value, btn1, btn2):
        if "slider-frame" == ctx.triggered_id:
            self.frame_idx = slider_value
        elif "btn-next" == ctx.triggered_id:
            self.frame_idx = min(self.frame_idx + 1,
                                 len(self.hololens_frames) - 1)
        elif "btn-prev" == ctx.triggered_id:
            self.frame_idx = max(self.frame_idx - 1, 0)
        # elif "interval" == ctx.triggered_id:
        #     self.frame_idx = n_intervals
        fig1 = px.imshow(
            self.hololens_frames[self.frame_idx  + self.hololens_hammer_point], binary_format="jpg")
        fig2 = px.imshow(
            self.cam1_frames[self.frame_idx + self.camera1_hammer_point], binary_format="jpg")
        fig3 = px.imshow(
            self.cam2_frames[(self.frame_idx + self.camera2_hammer_point)*2], binary_format="jpg")
        return fig1, fig2, fig3

    def update_plots(self, slider_value):
        fig = px.line(self.p1_df[self.mocap_hammer_point:(slider_value+1)*6 + self.mocap_hammer_point],
                      labels={'index': 'time (10ms)', 'value': 'pos'}, range_x=[0, 3000])
        return fig
    
    def sync_hammer(self, hololens_hammer_point, camera1_hammer_point, camera2_hammer_point, mocap_hammer_point):
        print("hololens_hammer_point", hololens_hammer_point)
        print("camera1_hammer_point", camera1_hammer_point)
        print("camera2_hammer_point", camera2_hammer_point)
        print("mocap_hammer_point", mocap_hammer_point)
        self.hololens_hammer_point = hololens_hammer_point
        self.camera1_hammer_point = camera1_hammer_point
        self.camera2_hammer_point = camera2_hammer_point 
        self.mocap_hammer_point = mocap_hammer_point
        return 0

    def run(self):
        console.print("Dash server started")
        self.app.run_server(debug=False)


if __name__ == '__main__':
    dps = DataProcessServer()
    dps.run()
