import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.path import Path
from fcsparser import parse
import json
import argparse


class FlowCytometryGating:
    def __init__(self, fcs_file, gate_hierarchy_file):
        self.fcs_file = fcs_file
        self.gate_hierarchy = self.load_gate_hierarchy(gate_hierarchy_file)
        self.data_df = self.read_transformed_fcs()
        self.data_df = self.add_unique_ids(self.data_df)
        self.labels = self.initialize_labels()
        self.current_indices = self.data_df.index

    def load_gate_hierarchy(self, gate_hierarchy_file):
        with open(gate_hierarchy_file, 'r') as file:
            gate_hierarchy = json.load(file)
        return gate_hierarchy

    def read_transformed_fcs(self):
        meta, data = parse(self.fcs_file, channel_naming='$PnN')
        print(f"Loaded transformed FCS file: {self.fcs_file}")
        return pd.DataFrame(data)

    def add_unique_ids(self, df):
        df['ID'] = np.arange(0, len(df))
        return df

    def initialize_labels(self):
        num_cells = len(self.data_df)
        labels = pd.DataFrame({
            'ID': self.data_df['ID'],
            **{gate['name']: np.full(num_cells, -1) for gate in self.flatten_hierarchy(self.gate_hierarchy)}
        })
        return labels

    def flatten_hierarchy(self, hierarchy):
        flat_list = []
        for gate in hierarchy:
            flat_list.append(gate)
            if 'children' in gate:
                flat_list.extend(self.flatten_hierarchy(gate['children']))
        return flat_list

    def custom_polygon_gate(self, data, x_channel, y_channel, vertices):
        path = Path(vertices)
        points = data[[x_channel, y_channel]].values
        gate_indices = path.contains_points(points)
        return gate_indices

    def apply_gates(self, hierarchy=None, parent_indices=None):
        if hierarchy is None:
            hierarchy = self.gate_hierarchy
            parent_indices = self.current_indices

        for gate in hierarchy:
            gate_mask = self.custom_polygon_gate(self.data_df.loc[parent_indices], gate['x_channel'], gate['y_channel'],
                                                 gate['vertices'])
            gate_indices = parent_indices[gate_mask]
            self.labels.loc[parent_indices, gate['name']] = 0
            self.labels.loc[gate_indices, gate['name']] = 1
            print(f"Applied {gate['name']} gate - number of 1s:", (self.labels[gate['name']] == 1).sum())
            print(f"{gate['name']} vertices: {gate['vertices']}")

            if 'children' in gate:
                self.apply_gates(gate['children'], gate_indices)

    def save_annotated_data(self, csv_file):
        combined_data = self.data_df.join(self.labels.set_index('ID'))
        combined_data.to_csv(csv_file, index=False)
        print("Annotated data saved to", csv_file)
        print("Combined data preview:")
        print(combined_data.head())

    def plot_with_contours(self, x, y, gate_name, vertices, title, with_contours=True):
        plt.figure(figsize=(10, 8))
        ax = sns.scatterplot(data=self.data_df, x=x, y=y, hue=(self.labels[gate_name] == 1),
                             palette={True: 'red', False: 'black'}, alpha=0.5, s=1)
        if with_contours:
            sns.kdeplot(data=self.data_df, x=x, y=y, fill=True, levels=10, color='blue', alpha=0.3)
        plt.gca().add_patch(plt.Polygon(vertices, closed=True, edgecolor='blue', fill=None))
        plt.title(title)
        plt.show()

    def plot_gates(self, with_contours=True):
        for gate in self.flatten_hierarchy(self.gate_hierarchy):
            self.plot_with_contours(gate['x_channel'], gate['y_channel'], gate['name'], gate['vertices'],
                                    f"{gate['name']} Gate", with_contours)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flow Cytometry Gating Tool")
    parser.add_argument("fcs_file", type=str, help="Path to the FCS file")
    parser.add_argument("gate_hierarchy_file", type=str, help="Path to the JSON file containing the gating hierarchy")
    parser.add_argument("output_csv_file", type=str, help="Path to save the annotated CSV file")
    parser.add_argument("--plot", action="store_true", help="Plot the gates")
    parser.add_argument("--with_contours", action="store_true", help="Plot gates with contours")

    args = parser.parse_args()

    gating_tool = FlowCytometryGating(args.fcs_file, args.gate_hierarchy_file)
    gating_tool.apply_gates()
    gating_tool.save_annotated_data(args.output_csv_file)

    if args.plot:
        gating_tool.plot_gates(with_contours=args.with_contours)
