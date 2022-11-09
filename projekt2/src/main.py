import os

from src.downloader import DataDownloader
from src.parser import DataParser
from src.dataanalysis import DataAnalysis

def main():
    downloader = DataDownloader()
    parser = DataParser(downloader.data_folder, downloader.data_files)

    analyzer = DataAnalysis(parser.df)
    print(analyzer.print_numerical_range())
    analyzer.print_categories_vars_unique()
    print(analyzer.chart_dir)
    analyzer.boxplot_males_females(show_fig=False,fig_location='BodyMassSpecies.png')
    analyzer.histogram_species_on_island(show_fig=False, fig_location='SpeciesOnIsland.png')
    analyzer.pair_grid(attr="Sex", palette={"FEMALE": "pink", "MALE": "skyblue"}, hue_order=["FEMALE", "MALE"],show_fig=False, fig_location='attrBySex.png')
    analyzer.pair_grid(show_fig=False, attr='Species',fig_location='attrBySpecies.png')
    analyzer.flipper_len_on_islands_kde(show_fig=False,fig_location='FlipperLenIslands.png')
    analyzer.swarmplot_sex_species(show_fig=False,fig_location='swarmplot.png')

if __name__ == "__main__":
    main()