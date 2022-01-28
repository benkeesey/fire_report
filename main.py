import os
import pandas as pd
import numpy as np

import firedb
import models
import visuals
import report_markdown as md

def historical_market_data():
    """
    Reads the historical data found in the data folder and manipulates it to just show market returns by year using the real value adjusted values.

    # Parameters:
    None
    
    # Returns:
    None
    """
    market_data_df = pd.read_csv(r'C:\Users\benjk\Documents\GitHub\fire_report\Data\ie_Data.csv', header=7)
    market_data_df = market_data_df.dropna(axis=1, how='all').dropna(axis=0, how='all')
    market_data_df = market_data_df.loc[market_data_df['Date'].notna()].copy()
    
    data_col_names = [
    'Date',
    'S&P_Comp_P',
    'Dividend',
    'Earnings',
    'CPI',
    'Date_Fraction',
    'Long_Interest_Rate_GS10',
    'Real_Price',
    'Real_Dividend',
    'Real_Total_Return_Price',
    'Real_Earnings',
    'Real_TR_Scaled_Earnings ',
    'CAPE',
    'TR_CAPE',
    'CAPE_Yield',
    'Monthly_Total_Bond_Returns',
    'Real_Total_Bond_Returns',
    '10_Year_Annualized_Stock_Real_Return',
    '10_Year_Annualized_Bond_Real_Return',
    'Real_10_Year_Excess_Annualized_Returns']
    
    market_data_df.columns = data_col_names
    market_data_df['Year'] = market_data_df['Date'].apply(np.floor).astype(int)
    market_data_df['Real_Total_Return_Price'] = market_data_df['Real_Total_Return_Price'].str.strip().str.replace(',','').astype(float)
    
    # Calculate the monthly returns. Currently only implementing the yearly returns, but this could be used to increase model resolution.
    market_data_df['Real_Monthly_Return'] = market_data_df['Real_Total_Return_Price'].diff()
    market_data_df['Real_Monthly_Return_Percentage'] = (market_data_df['Real_Monthly_Return']/market_data_df['Real_Total_Return_Price'])*100
    
    yearly_market_df = pd.DataFrame()
    yearly_market_df['start_Real_Price'] = market_data_df.groupby('Year')['Real_Total_Return_Price'].first()
    yearly_market_df['end_Real_Price'] = market_data_df.groupby('Year')['Real_Total_Return_Price'].last()
    yearly_market_df['Real_Return_Percentage'] = ((yearly_market_df['end_Real_Price'] - yearly_market_df['start_Real_Price'])/yearly_market_df['start_Real_Price'])*100
    
    return yearly_market_df


def main(user_id=None):
    
    """
    The main function of the fire_report will call the mysql db or take in the input file to gather the required information to create the model, the plots and the dashboard.
    Here is brief description of each of the required parameters:

    # Personal Financial parameters.
    yearly_savings = Yearly Savings you plan to contribute to your accounts. NOTE: This is a Gross amount before tax.
    growth_comparison_starting_balance = starting balance used in the (apples to apples) comparison of showing growth between accounts and cash investment.
    time_window = time in years you want to model. Years spend contributing and withdrawing from accounts is calculated using your current age and your retirement age within this time window
    yearly_HSA_qualified_expense = Yearly estimate of qualifing HSA medical expenses. These will be treated as dollars you are able to withdraw without penalty from the HSA account. (currently this is just a static yearly value)
    age = The current age of the person
    retirement_age = The age the person plans of retiring. At this age they will stop contributing to their accounts and start withdrawing from them instead as spending.
    retirement_spend = Value person plans on spending per year in retirement (All calculated values are in Current Real Dollars.)

    balance_brokerage = Currently balance in Brokerage accounts. Used in combined Liquid & Net worth Backtesting Plots
    balance_401k = Currently balance in Traditional 401k accounts. Used in combined Liquid & Net worth Backtesting Plots
    balance_HSA = Currently balance in HSA accounts. Used in combined Liquid & Net worth Backtesting Plots
    balance_roth = Currently balance in Roth 401k accounts. Used in combined Liquid & Net worth Backtesting Plots 

    balance_HSA_qualified_expense = Currently balance of qualified medical expenses in HSA accounts. Used in combined Liquid & Net worth Backtesting Plots
    balance_401k_contributions = Currently balance of contributions made to Traditonal 401k accounts.This is needed to help calculate the Capital Gains tax once retirement age is reached. Deposits need to be taken into account that were already made. Used in combined Liquid & Net worth Backtesting Plots NOTE: This should be 0 if balance_401k is also 0.
    
    # Investment growth parameters.
    HSA_contribution_limit = HSA contribution limit to use for the entire funding period in current Pre-Tax dollars.
    Roth_contribution_limit = Roth contribution limit to use for the entire funding period in current Post-Tax dollars.
    Traditional_401k_contribution_limit = Traditional 401k contribution limit to use for the entire funding period in current Pre-Tax dollars.
    Expense_Ratio = Expense Ratio Investments charge across all accounts as a percent. This model assumes the same investment strategy is evenly applied across all accounts.
    Marginal_Tax_Rate = Current Marginal Tax Rate as a percent to be applied to all investment earnings.
    Capital_Gains_Tax = Current Capital Gains Tax rate as a percent to be applied to all investment earnings.
    Retired_Marginal_Tax_Rate = Marginal Tax Rate as a percent to be applied to all investment earnings at retirement age.
    Retired_Capital_Gains_Tax = Capital Gains Tax as a percent to be applied to all investment earnings at retirement age.

    # Visual parameters.
    color_scheme = Color Scheme for the generated report.

    # Parameters:
    user_id : str, default None
        user id string that can be passed instead of the input excel file if the user information is already stored in the mysql db.
    
    # Returns:
    None
    """
    
    # Get Historical yearly market data
    yearly_market_df = firedb.get_market_data()
    # Old method that does not pull historical data from mysql db
    # yearly_market_df = historical_market_data()

    try:
        if user_id != None:
            user_vars_dict = firedb.return_user_profile(user_id).T.to_dict()[0]
        else:
            user_var_series = pd.read_excel(r'Data\input.xlsx', sheet_name='Input Parameters', index_col=1).drop('Unnamed: 0',axis=1)['Value']
            user_vars_dict = user_var_series.to_dict()

            # NOTE: Could use UUID here or better method for uniquely identifying user. But this isn't really needed currently.
            # Checks if the input template has been filled out. If it has it loads the new user information into the mysql db with a unique id from the name, age, and retirement_age.
            user_id = str(user_var_series['name']) + str(user_var_series['age']) + str(user_var_series['retirement_age'])
            user_var_series['user_id'] =  user_id
            # Add new user info to mysql db
            firedb.load_new_user_profile(user_var_series)
    
    # If there is no input excel sheet just use some default values
    except:
        default_profile = firedb.return_user_profile('John3055')
        user_vars_dict = default_profile.T.to_dict()[0]

    # Initialize the Model class with the user defined variables.
    Model_instance = models.Model(**user_vars_dict)
    # Create the Dataset models used of growth data for an HSA and a Brokerage account to use for the Backtesting_Plot_Growth_Comparison Plot
    HSA_models_df, HSA_models_liquid_df = Model_instance.Backtest_Growth_Models('HSA', yearly_market_df)
    Brokerage_models_df, Brokerage_models_liquid_df = Model_instance.Backtest_Growth_Models('Brokerage', yearly_market_df)
    # Get DataFrame of cash deposits that will be plotted in the comparison plot
    cash_balance_df = Model_instance.cash_balance()

    # Initialize the Visualization class with the user defined variables.
    visual_param_dict = {k:user_vars_dict[k] for k in ('name','time_window','color_scheme') if k in user_vars_dict}
    Visuals_instance = visuals.Visualization(**visual_param_dict)

    # Create instance of Visualization that inherits methods from models.Model to create visualizations and Dashboard
    Visuals_instance.Backtesting_Plot_Growth_Comparison(account1=HSA_models_df, 
        account1_name='HSA', account2=Brokerage_models_df, account2_name='Brokerage', cash_account=cash_balance_df)


    # Use the inherited method to calculate Total Spending Net and Liquid Assets DataFrames
    Total_Net_Return_Spending_df, Total_Liquid_Return_Spending_df = Model_instance.Backtest_Plot_Spending(yearly_market_df)

    # Create total Net and Liquid Spending plots and save them to the Assets folder.
    Visuals_instance.spending_fire_plot(df=Total_Net_Return_Spending_df, file_name=f"Assets/{Visuals_instance.name}'s Net Backtesting Plot")
    Visuals_instance.spending_fire_plot(df=Total_Liquid_Return_Spending_df, file_name=f"Assets/{Visuals_instance.name}'s Liquid Backtesting Plot")

    # Call Dashboard method to produce final dashboard. The liquid and net DataFrames are needed to calculate statistics to display.
    Visuals_instance.Dashboard(Total_Liquid_Return_Spending_df, Total_Net_Return_Spending_df)


if __name__ == "__main__":
    main()


