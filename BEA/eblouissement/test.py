import pandas as pd
import numpy as np
from classPoint import Point
from classTrajectoire import Trajectoire


if __name__ == "__main__":
    cd = "flightdata.csv"
    traj = Trajectoire(cd)
    t = traj.get_df_pts()
    d = traj.get_list_pts()