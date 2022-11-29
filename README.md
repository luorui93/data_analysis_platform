# data_analysis_platform

Data analysis platforms for viewing multimodal sensor data developed in [Dash](https://dash.plotly.com/introduction).

## Setup
1. Python > 3.6 is required.

2. Anaconda or other similar virtual environment is recommended.

3. Run `pip install -r requirements.txt` to install Python modules.


## Usage
### Fish Cutting Analysis
1. Navigate to `fish_cutting_analysis` folder and run `python app.py`

2. A file selection gui will pop up, select the data that contains the trial data, for example `<path_to_data>/trial1`. 
   Make sure the mocap data `*.mat` is also in the corresponding folder.

3. Visit http://127.0.0.1:8050/ in your web browser.

4. You can set the hammer time for the camera view or mocap to sync data.



## TODO
- [ ] Find faster methods to display video frames
- [ ] Maybe more elegant way to select data folders
- [ ] 3D plot support