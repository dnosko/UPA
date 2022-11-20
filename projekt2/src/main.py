import os

from src.downloader import DataDownloader
from src.parser import DataParser
from src.dataanalysis import DataAnalysis
from src.datamining import DataMiner


def make_charts(analyzer, show=False):
    analyzer.boxplot_males_females(show_fig=show, fig_location='BodyMassSpecies.png')
    analyzer.histogram_species_on_island(show_fig=show, fig_location='SpeciesOnIsland.png')
    analyzer.pair_grid(attr="Sex", palette={"FEMALE": "pink", "MALE": "skyblue"}, hue_order=["FEMALE", "MALE"],
                       show_fig=show, fig_location='attrBySex.png')
    analyzer.pair_grid(show_fig=show, attr='Species', fig_location='attrBySpecies.png')
    analyzer.flipper_len_on_islands_kde(show_fig=show, fig_location='FlipperLenIslands.png')
    analyzer.swarmplot_sex_species(show_fig=show, fig_location='swarmplot.png')


def find_outliers(analyzer, show=False):
    analyzer.find_outliers_3sigma(df=analyzer.numerical, show_fig=show, fig_location='outliers.png')
    analyzer.find_outliers_sex('male', show_fig=show, fig_location='outliersMales.png')
    analyzer.find_outliers_sex('female', show_fig=show, fig_location='outliersFemales.png')
    analyzer.find_outliers_species('Adelie', show_fig=show, fig_location='outliersAdelie.png')
    analyzer.find_outliers_species('Chinstrap', show_fig=show, fig_location='outliersChinstrap.png')
    analyzer.find_outliers_species('Gentoo', show_fig=show, fig_location='outliersGentoo.png')
    analyzer.find_outliers_IQR(analyzer.df)

def correlation(analyzer):
    df_all = analyzer.numerical.drop(['Sample Number'], axis=1)
    corr = analyzer.correlation(df_all)
    print('Correlation all species\n', corr.round(3).to_string())
    analyzer.correlation_chart(df_all, show_fig=False, fig_location='corr.png')
    penguins = ['Adelie', 'Gentoo', 'Chinstrap']
    for p in penguins:
        analyzer.correlation_species(p)

def main():
    downloader = DataDownloader()
    parser = DataParser(downloader.data_folder, downloader.data_files)

    analyzer = DataAnalysis(parser.df)
    analyzer.analyze_attributes()
    make_charts(analyzer, show=False)
    analyzer.find_missing_values()
    find_outliers(analyzer, show=False)
    correlation(analyzer)


    miner = DataMiner(parser.df)
    miner.resolve_missing_values()
    miner.transformations()
    
if __name__ == "__main__":
    main()
