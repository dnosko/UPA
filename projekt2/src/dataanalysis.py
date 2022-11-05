import pandas as pd


class DataAnalysis:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.types = self.df.dtypes
        self.change_df_types()
        self.numerical = self.df.select_dtypes(include='number')
        self.categories = self.df.select_dtypes(include='category')
        self.timestamps = self.df.select_dtypes(include='timedelta')
        self.numerical_analysis = self.numerical_analysis(self.numerical)
        self.categories_values = self.get_categories_values(self.categories)

    def change_df_types(self):
        self.df['Timestamp'] = pd.to_datetime(self.df['Timestamp'])
        objects_df = self.df.select_dtypes(include="object")

        for i in objects_df.columns:
            self.df[i] = self.df[i].astype("category")

    def numerical_analysis(self, df):
        return df.agg({'min', 'max', 'mean', 'median'})

    def print_numerical_range(self):
        print(self.numerical_analysis.transpose().to_string())

    def print_categorical_range(self):
        print(self.categories_values.to_string())


    def analyze_attribute(self):
        avg_num = self.df.mean(numeric_only=True)
        median_num = self.df.median(numeric_only=True)
        max_num = self.df.max(numeric_only=True)
        min_num = self.df.min(numeric_only=True)

        self.print_numerical_range()
        self.print_categorical_range()

    def get_min_max(self, df):
        pass

    def get_categories_values(self, categories):
        cat_vals_dic = {}
        for i in categories.columns:
            cat_vals_dic[i] = categories[i].value_counts()

        df = pd.DataFrame(cat_vals_dic.values(), index=list(cat_vals_dic.keys())).stack()
        df = pd.DataFrame(df).rename(columns={0: 'counts'})
        #print(df.to_string())
        # print(df.groupby(level=0, group_keys=True).agg{}.to_string())
        return df
