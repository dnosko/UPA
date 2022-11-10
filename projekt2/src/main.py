import os

from src.downloader import DataDownloader
from src.parser import DataParser
from src.dataanalysis import DataAnalysis


def make_charts(analyzer, show=False):
    analyzer.boxplot_males_females(show_fig=show, fig_location='BodyMassSpecies.png')
    analyzer.histogram_species_on_island(show_fig=show, fig_location='SpeciesOnIsland.png')
    analyzer.pair_grid(attr="Sex", palette={"FEMALE": "pink", "MALE": "skyblue"}, hue_order=["FEMALE", "MALE"],
                       show_fig=show, fig_location='attrBySex.png')
    analyzer.pair_grid(show_fig=show, attr='Species', fig_location='attrBySpecies.png')
    analyzer.flipper_len_on_islands_kde(show_fig=show, fig_location='FlipperLenIslands.png')
    analyzer.swarmplot_sex_species(show_fig=show, fig_location='swarmplot.png')


def find_outliers(analyzer, show=False):
    analyzer.find_outliers(df=analyzer.numerical, show_fig=show, fig_location='outliers.png')
    analyzer.find_outliers_sex('male', show_fig=show, fig_location='outliersMales.png')
    analyzer.find_outliers_sex('female', show_fig=show, fig_location='outliersFemales.png')
    analyzer.find_outliers_species('Adelie', show_fig=show, fig_location='outliersAdelie.png')
    analyzer.find_outliers_species('Chinstrap', show_fig=show, fig_location='outliersChinstrap.png')
    analyzer.find_outliers_species('Gentoo', show_fig=show, fig_location='outliersGentoo.png')


def print_dataset_info(analyzer):
    analyzer.print_numerical_range()
    analyzer.print_categories_vars_unique()


def main():
    downloader = DataDownloader()
    parser = DataParser(downloader.data_folder, downloader.data_files)

    analyzer = DataAnalysis(parser.df)
    print_dataset_info(analyzer)
    make_charts(analyzer, show=False)
    analyzer.find_missing_values()
    find_outliers(analyzer, show=False)


if __name__ == "__main__":
    main()
