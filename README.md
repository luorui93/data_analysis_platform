# data_analysis_platform

Data analysis platforms for viewing multimodal sensor data developed in [Dash](https://dash.plotly.com/introduction).

![Data analysis platform user interface](/demo.gif)

## Setup
1. Python >= 3.6 is required.

2. Anaconda or other similar virtual environment is recommended.
 
3. Install Python modules dependencies.
```
pip install -r requirements.txt
``` 
If the auto install failed, you may try to install pakcages manually, e.g. `pip install rich`

## Workspace layout
To run this data analysis tool, your workspace layout should look like this:
```
Workspace/
├── data_analysis_platform/
│   ├── fish_cutting_analysis/
│   │   ├── assets
│   │   └── app.py
│   ├── data_preprocess.py
│   ├── README.md
│   └── requirements.txt
└── data/
    ├── trial1/
    │   ├── cam_1-color-image_raw
    │   ├── cam_2-rgb-image_rect_color
    │   ├── ...
    │   └── Trial1_Cut_Fillets_Move_Toss.mat
    ├── trial2/
    │   └── ...
    └── ...
```

## Usage
### Data Preprocess
Some of the data might require preprocessing such as naming correction and color correction. Simply run
```
python data_preprocess.py
```
and follow the prompts to execute the functions you want.
### Fish Cutting Analysis
1. Navigate to `fish_cutting_analysis` folder and run 
```
python app.py
```

2. A folder selection gui will pop up, select the data that contains the trial data, for example `<path_to_data>/trial1`. 
   Make sure the mocap data `*.mat` is also in the corresponding folder.
   
![](/data_selection.gif)

3. Visit http://127.0.0.1:8050/ in your web browser.

4. Drag the slider will fast forward the frames. The slider value is currently in milliseconds. 
   You can set the hammer time for the camera view or mocap to sync data.



## TODO
- [ ] Find faster methods to display video frames
- [ ] Maybe more elegant way to select data folders
- [ ] 3D plot support
