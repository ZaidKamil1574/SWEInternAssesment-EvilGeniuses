import pandas as pd
import json

#1.	Write a python class called ProcessGameState
# Define the ProcessGameState class
class ProcessGameState:
    #Qusetion 1.a.
    # Initialization method that gets called when a class object is created
    def __init__(self, file_path):
        # Load the Parquet file into a pandas DataFrame
        self.df = pd.read_parquet(file_path)

    #Qusetion 1.b.
    # Method to check if a point lies within the defined boundary
    def point_in_polygon(self, x, y, poly):
        # Checks if a point is inside a polygon
        num = len(poly)
        i = 0
        j = num - 1
        c = False
        for i in range(num):
            if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                    (x < poly[i][0] + (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
                     (poly[j][1] - poly[i][1])):
                c = not c
            j = i
        return c

    # Method to filter data within the boundary
    def filter_by_boundary(self, boundary_coords, z_bounds):
        # For each row in the DataFrame, apply the point_in_polygon method
        self.df['in_boundary'] = self.df.apply(
            lambda row: self.point_in_polygon(row['X'], row['Y'], boundary_coords) and z_bounds[0] <= row['Z'] <=
                        z_bounds[1], axis=1)

    #Qusetion 1.c.
    # Method to extract weapons from the inventory JSON column
    def extract_weapons(self):
        # Parse the 'inventory' column and extract weapon information
        def parse_inventory(inv):
            weapons = [item['item_type'] for item in json.loads(inv)]
            return weapons

        self.df['weapons'] = self.df['inventory'].apply(parse_inventory)


# Instantiate the ProcessGameState object with the file path
file_path = "game_state_frame_data.parquet"
game_state = ProcessGameState(file_path)

# Specify boundary coordinates and Z bounds
boundary_coords = [[-1735, 250], [-2024, 398], [-2806, 742], [-2472, 1233], [-1565, 580]]
z_bounds = [285, 421]

#Question 2.a
# Apply the filtering and weapons extraction methods
game_state.filter_by_boundary(boundary_coords, z_bounds)
team2_T_in_boundary = game_state.df[(game_state.df['team'] == 'Team2') & (game_state.df['side'] == 'T') & (game_state.df['in_boundary'])]
common_strategy = len(team2_T_in_boundary) / len(game_state.df[(game_state.df['team'] == 'Team2') & (game_state.df['side'] == 'T')]) > 0.5

#Question 2.b
# Calculate the proportion of times Team 2 on T side entered the boundary
game_state.extract_weapons()
team2_T_in_boundary = game_state.df[
    (game_state.df['team'] == 'Team2') & (game_state.df['side'] == 'T') & (game_state.df['in_boundary'])]
common_strategy = len(team2_T_in_boundary) / len(
    game_state.df[(game_state.df['team'] == 'Team2') & (game_state.df['side'] == 'T')]) > 0.5

# Calculate the average timer for Team 2 on T side entering Bombsite B with at least 2 rifles or SMGs
team2_T_in_B = game_state.df[(game_state.df['team'] == 'Team2') & (game_state.df['side'] == 'T') &
                             (game_state.df['areaname'] == 'BombsiteB') & (
                                 game_state.df['weapons'].apply(lambda weapons: weapons.count('rifle') +
                                                                                weapons.count('smg') >= 2))]
average_timer = team2_T_in_B['clocktime'].mean()


#Question 2.c
# Generate a heatmap of positions of Team 2 on CT side in Bombsite B
import seaborn as sns
import matplotlib.pyplot as plt

team2_CT_in_B = game_state.df[(game_state.df['team'] == 'Team2') & (game_state.df['side'] == 'CT') & (game_state.df['areaname'] == 'BombsiteB')]
plt.figure(figsize=(10,10))
sns.heatmap(team2_CT_in_B[['X', 'Y']].pivot_table(index='Y', columns='X', aggfunc=len, fill_value=0), cmap='viridis')
plt.title('Heatmap of Team2 CT positions in BombsiteB')
plt.show()