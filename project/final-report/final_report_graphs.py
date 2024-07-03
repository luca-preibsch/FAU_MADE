import sqlite3
import statistics
import sys

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy.stats import linregress

db_path = '../../data/data.sqlite'
plot_path = ''
db_conn = sqlite3.connect(db_path)
saveToPGF = sys.argv.__len__() >= 1 and sys.argv.__contains__("save")

if saveToPGF:
    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        # "font.size": 100,  # Set the desired font size here
        "axes.labelsize": 20,
        "xtick.labelsize": 15,
        "ytick.labelsize": 15,
        "legend.fontsize": 20,
        # "figure.titlesize": 100,
        # Additional settings to use LaTeX fonts
        # "font.family": "serif",
        # "text.usetex": True,
        # "pgf.rcfonts": False,
    })


def output_plot(plt, function, country_code=None):
    if saveToPGF:
        plt.tight_layout()

        if country_code:
            country_code = f"_{country_code}"
        else:
            country_code = ""

        plt.savefig(f"{plot_path}{function.__name__}{country_code}.pgf")
    else:
        plt.show()


def plot_net_greenhouse_gas_emissions():
    query = """
    SELECT geo, year, value
    FROM emissions
    """
    df = pd.read_sql(query, db_conn)

    pivot_df = df.pivot(index='year', columns='geo', values='value')

    plt.figure(figsize=(12, 8))

    for country in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[country], label=country)

    plt.xlabel('Year')
    plt.ylabel('Tonnes per capita')
    plt.title('Greenhouse Gas Emissions Over Time')
    plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    output_plot(plt, plot_primary_energy_consumption)


def plot_primary_energy_consumption():
    query = """
    SELECT geo, year, value
    FROM energy_consumption
    """
    df = pd.read_sql(query, db_conn)

    pivot_df = df.pivot(index='year', columns='geo', values='value')

    plt.figure(figsize=(12, 8))

    for country in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[country], label=country)

    plt.xlabel('Year')
    plt.ylabel('Tonnes of oil equivalent (TOE) per capita')
    plt.title('Primary Energy Consumption Over Time')
    plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    output_plot(plt, plot_primary_energy_consumption)


def plot_share_of_energy_from_renewable_sources():
    query = """
    SELECT geo, year, value
    FROM energy_share
    """
    df = pd.read_sql(query, db_conn)

    pivot_df = df.pivot(index='year', columns='geo', values='value')

    plt.figure(figsize=(12, 8))

    for country in pivot_df.columns:
        plt.plot(pivot_df.index, pivot_df[country], label=country)

    plt.xlabel('Year')
    plt.ylabel('%')
    plt.title('Share of Energy From Renewable Sources Over Time')
    plt.legend(title='Country', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout()
    output_plot(plt, plot_share_of_energy_from_renewable_sources)


def plot_correlation_emissions_to_consumption():
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])

    merged_df['year'] = merged_df['year'].astype(int)

    unique_years = merged_df['year'].unique()
    plt.figure(figsize=(15, 10))

    for year in unique_years:
        yearly_data = merged_df[merged_df['year'] == year]
        plt.scatter(yearly_data['energy_consumption'], yearly_data['emissions'], label=f'Year {year}', alpha=0.6)

    # Highlight some outliers or high consumption countries
    outliers = merged_df[merged_df['energy_consumption'] > 10]
    for i, row in outliers.iterrows():
        plt.annotate(row['geo'], (row['energy_consumption'], row['emissions']), textcoords="offset points",
                     xytext=(0, 10), ha='center')

    plt.title('Correlation between Energy Consumption and Greenhouse Gas Emissions Over Time')
    plt.xlabel('Energy Consumption (tonnes of oil equivalent per capita)')
    plt.ylabel('Greenhouse Gas Emissions (tonnes per capita)')
    plt.legend()
    plt.grid(True)
    output_plot(plt, plot_correlation_emissions_to_consumption)


def plot_correlation_emissions_to_consumption_single_country(country_code="DE"):
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])

    germany_df = merged_df[merged_df['geo'] == 'DE']

    germany_df = germany_df.sort_values(by='year')

    plt.figure(figsize=(10, 6))
    plt.plot(germany_df['energy_consumption'], germany_df['emissions'], marker='o', linestyle='-')

    for i, row in germany_df.iterrows():
        plt.annotate(row['year'], (row['energy_consumption'], row['emissions']),
                     textcoords="offset points", xytext=(0, 10), ha='center')

    plt.title('Correlation between Energy Consumption and Greenhouse Gas Emissions in Germany Over Time')
    plt.xlabel('Energy Consumption (tonnes of oil equivalent per capita)')
    plt.ylabel('Greenhouse Gas Emissions (tonnes per capita)')
    plt.grid(True)
    output_plot(plt, plot_correlation_emissions_to_consumption_single_country)


def plot_scatter_with_linear_reg():
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])

    germany_df = merged_df[merged_df['geo'] == 'DE']

    germany_df = germany_df.sort_values(by='year')

    plt.figure(figsize=(10, 6))
    sns.regplot(x='energy_consumption', y='emissions', data=germany_df, marker='o')

    # Annotate the years
    for i, row in germany_df.iterrows():
        plt.annotate(row['year'], (row['energy_consumption'], row['emissions']),
                     textcoords="offset points", xytext=(0, 10), ha='center')

    plt.title('Correlation between Energy Consumption and Greenhouse Gas Emissions in Germany')
    plt.xlabel('Energy Consumption (tonnes of oil equivalent per capita)')
    plt.ylabel('Greenhouse Gas Emissions (tonnes per capita)')
    plt.grid(True)
    output_plot(plt, plot_scatter_with_linear_reg)


def plot_multi_country_regression():
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])

    g = sns.FacetGrid(merged_df, col="geo", col_wrap=4, height=4, sharex=False, sharey=False)
    g.map_dataframe(sns.regplot, x='energy_consumption', y='emissions', marker='o')

    rs = []

    # Annotate each plot with the correlation coefficient
    for ax, geo in zip(g.axes, merged_df['geo'].unique()):
        country_data = merged_df[merged_df['geo'] == geo]
        slope, intercept, r_value, p_value, std_err = linregress(country_data['energy_consumption'],
                                                                 country_data['emissions'])
        ax.annotate(f'r = {r_value:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', ha='left', va='top', fontsize=10,
                    color='red')
        rs.append(r_value)

    g.set_titles("{col_name}")
    g.set_axis_labels("Energy Consumption (tonnes of oil equivalent per capita)",
                      "Greenhouse Gas Emissions (tonnes per capita)")

    plt.subplots_adjust(top=0.9)
    g.fig.suptitle('Correlation between Energy Consumption and Greenhouse Gas Emissions for Different Countries')

    output_plot(plt, plot_multi_country_regression)
    print(f"median r: {statistics.median(rs)}")


def plot_global_regression():
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])

    plt.figure(figsize=(10, 6))
    slope, intercept, r_value, p_value, std_err = linregress(merged_df['energy_consumption'], merged_df['emissions'])
    sns.regplot(x='energy_consumption', y='emissions', data=merged_df, marker='o', scatter_kws={'s': 10},
                label=f'r = {r_value:.2f}')

    # Calculate the correlation coefficient and p-value
    # slope, intercept, r_value, p_value, std_err = linregress(merged_df['energy_consumption'], merged_df['emissions'])
    # plt.annotate(f'r = {r_value:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', ha='left', va='top', fontsize=12, color='red')
    # plt.plot(merged_df['energy_consumption'], intercept + slope * merged_df['energy_consumption'], 'b', label=f'r = {r_value:.2f}')

    # plt.title('Global Correlation between Energy Consumption and Greenhouse Gas Emissions')
    plt.xlabel('Energy Consumption (tonnes of oil equivalent per capita)')
    plt.ylabel('Greenhouse Gas Emissions (tonnes per capita)')
    plt.legend()
    plt.grid(True)
    output_plot(plt, plot_global_regression)


def plot_country_data_with_renewables(country_code):
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"
    energy_share_query = "SELECT geo, year, value AS renewable_share FROM energy_share"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)
    energy_share_df = pd.read_sql(energy_share_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])
    merged_df = pd.merge(merged_df, energy_share_df, on=['geo', 'year'])

    country_df = merged_df[merged_df['geo'] == country_code]

    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(country_df['energy_consumption'], country_df['emissions'],
                          c=country_df['renewable_share'], cmap='viridis', s=100, alpha=0.7, edgecolors='w',
                          linewidth=0.5)

    slope, intercept, r_value, p_value, std_err = linregress(country_df['energy_consumption'], country_df['emissions'])
    plt.plot(country_df['energy_consumption'], intercept + slope * country_df['energy_consumption'], 'r',
             label=f'r = {r_value:.2f}')

    cbar = plt.colorbar(scatter)
    cbar.set_label('Share of Renewable Energy (%)')

    # plt.title(f'Energy Consumption vs. Greenhouse Gas Emissions with Renewable Energy Share for {country_code}')
    plt.xlabel('Energy Consumption (tonnes of oil equivalent per capita)')
    plt.ylabel('Greenhouse Gas Emissions (tonnes per capita)')
    plt.legend()
    plt.grid(True)
    output_plot(plt, plot_country_data_with_renewables, country_code)


def plot_global_data_with_renewables():
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"
    energy_share_query = "SELECT geo, year, value AS renewable_share FROM energy_share"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)
    energy_share_df = pd.read_sql(energy_share_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])
    merged_df = pd.merge(merged_df, energy_share_df, on=['geo', 'year'])

    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(merged_df['energy_consumption'], merged_df['emissions'],
                          c=merged_df['renewable_share'], cmap='viridis', s=50, alpha=0.7, edgecolors='w',
                          linewidth=0.5)

    slope, intercept, r_value, p_value, std_err = linregress(merged_df['energy_consumption'], merged_df['emissions'])
    plt.plot(merged_df['energy_consumption'], intercept + slope * merged_df['energy_consumption'], 'r',
             label=f'r = {r_value:.2f}')

    cbar = plt.colorbar(scatter)
    cbar.set_label('Share of Renewable Energy (%)')

    # outliers = merged_df[merged_df['renewable_share'] > 50]
    # for i in range(len(outliers)):
    #     plt.annotate(outliers.iloc[i]['geo'],
    #                  (outliers.iloc[i]['energy_consumption'], outliers.iloc[i]['emissions']),
    #                  textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)

    # plt.title('Global Correlation between Energy Consumption and Greenhouse Gas Emissions with Renewable Energy Share')
    plt.xlabel('Energy Consumption (tonnes of oil equivalent per capita)')
    plt.ylabel('Greenhouse Gas Emissions (tonnes per capita)')
    plt.legend()
    plt.grid(True)
    output_plot(plt, plot_global_data_with_renewables)


def plot_renewables_vs_emissions(country_code=None):
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"
    energy_share_query = "SELECT geo, year, value AS renewable_share FROM energy_share"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)
    energy_share_df = pd.read_sql(energy_share_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])
    merged_df = pd.merge(merged_df, energy_share_df, on=['geo', 'year'])

    filtered_df = merged_df
    if country_code:
        filtered_df = merged_df[merged_df['geo'] == country_code]

    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(filtered_df['renewable_share'], filtered_df['emissions'],
                          c=filtered_df['energy_consumption'], cmap='viridis', s=50, alpha=0.7, edgecolors='w',
                          linewidth=0.5)

    slope, intercept, r_value, p_value, std_err = linregress(filtered_df['renewable_share'], filtered_df['emissions'])
    plt.plot(filtered_df['renewable_share'], intercept + slope * filtered_df['renewable_share'], 'r',
             label=f'r = {r_value:.2f}')

    cbar = plt.colorbar(scatter)
    cbar.set_label('Energy Consumption (tonnes of oil equivalent per capita)')

    # title = 'Correlation between Share of Renewable Energy and Greenhouse Gas Emissions'
    # if country_code:
    #     title += f' in {country_code}'
    # else:
    #     title += ' in All Countries'
    # plt.title(title)
    plt.xlabel('Share of Renewable Energy (%)')
    plt.ylabel('Greenhouse Gas Emissions (tonnes per capita)')
    plt.legend()
    plt.grid(True)
    output_plot(plt, plot_renewables_vs_emissions)


def plot_renewables_vs_emissions_for_all_countries():
    emissions_query = "SELECT geo, year, value AS emissions FROM emissions"
    energy_consumption_query = "SELECT geo, year, value AS energy_consumption FROM energy_consumption"
    energy_share_query = "SELECT geo, year, value AS renewable_share FROM energy_share"

    emissions_df = pd.read_sql(emissions_query, db_conn)
    energy_consumption_df = pd.read_sql(energy_consumption_query, db_conn)
    energy_share_df = pd.read_sql(energy_share_query, db_conn)

    merged_df = pd.merge(emissions_df, energy_consumption_df, on=['geo', 'year'])
    merged_df = pd.merge(merged_df, energy_share_df, on=['geo', 'year'])

    g = sns.FacetGrid(merged_df, col="geo", col_wrap=4, height=4, sharex=False, sharey=False)
    g.map_dataframe(sns.scatterplot, x='renewable_share', y='emissions', hue='energy_consumption', palette='viridis',
                    marker='o', edgecolor='w', linewidth=0.5)

    rs = []

    for ax, geo in zip(g.axes.flat, merged_df['geo'].unique()):
        country_data = merged_df[merged_df['geo'] == geo]
        slope, intercept, r_value, p_value, std_err = linregress(country_data['renewable_share'],
                                                                 country_data['emissions'])
        ax.plot(country_data['renewable_share'], intercept + slope * country_data['renewable_share'], 'r')
        ax.annotate(f'r = {r_value:.2f}', xy=(0.05, 0.95), xycoords='axes fraction', ha='left', va='top', fontsize=10,
                    color='red')
        rs.append(r_value)

    g.set_titles("{col_name}")
    g.set_axis_labels("Share of Renewable Energy (%)", "Greenhouse Gas Emissions (tonnes per capita)")

    plt.subplots_adjust(top=0.9)
    g.fig.suptitle('Correlation between Share of Renewable Energy and Greenhouse Gas Emissions for Different Countries')

    print(f"median r in share {statistics.median(rs)}")
    output_plot(plt, plot_renewables_vs_emissions_for_all_countries)


def main():
    # plot data sources
    # plot_net_greenhouse_gas_emissions()
    # plot_primary_energy_consumption()
    # plot_share_of_energy_from_renewable_sources()

    # plot correlations
    # plot_correlation_emissions_to_consumption() # trash
    # plot_correlation_emissions_to_consumption_single_country() # trash
    plot_scatter_with_linear_reg()
    plot_multi_country_regression()
    plot_global_regression()
    plot_country_data_with_renewables('LU')
    # plot_country_data_with_renewables('SI')
    plot_country_data_with_renewables('AT')
    plot_global_data_with_renewables()
    plot_renewables_vs_emissions()  # Reflektion? Grenze?
    # plot_renewables_vs_emissions('SI')
    # plot_renewables_vs_emissions('DE')
    # plot_renewables_vs_emissions('LU')
    # plot_renewables_vs_emissions('HU')
    plot_renewables_vs_emissions_for_all_countries()

    # clean up
    db_conn.close()


if __name__ == '__main__':
    main()
