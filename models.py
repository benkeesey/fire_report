import pandas as pd
import numpy as np


class Model(object):
    def __init__(self, name, age, retirement_age, yearly_savings
    , time_window, retirement_spend, yearly_HSA_qualified_expense
    , balance_brokerage, balance_HSA, balance_401k, balance_roth
    , balance_HSA_qualified_expense, balance_401k_contributions
    , growth_comparison_starting_balance, HSA_contribution_limit
    , Roth_contribution_limit, Traditional_401k_contribution_limit
    , Expense_Ratio, Marginal_Tax_Rate, Capital_Gains_Tax
    , Retired_Marginal_Tax_Rate, Retired_Capital_Gains_Tax, **argd):
        """
        Constructs all the necessary attributes for the fire report from the passed dict.
        Otherwise we will define some instance default values.
        """
        self.name = name
        self.age = age
        self.retirement_age = retirement_age
        self.retirement_spend = retirement_spend
        self.yearly_savings = yearly_savings
        self.growth_comparison_starting_balance = growth_comparison_starting_balance
        self.time_window = time_window
        self.yearly_HSA_qualified_expense = yearly_HSA_qualified_expense
        self.balance_brokerage = balance_brokerage
        self.balance_HSA = balance_HSA
        self.balance_401k = balance_401k
        self.balance_roth = balance_roth
        self.balance_HSA_qualified_expense = balance_HSA_qualified_expense
        self.balance_401k_contributions = balance_401k_contributions
        self.HSA_contribution_limit = HSA_contribution_limit
        self.Roth_contribution_limit = Roth_contribution_limit
        self.Traditional_401k_contribution_limit = Traditional_401k_contribution_limit
        self.Expense_Ratio = Expense_Ratio
        self.Marginal_Tax_Rate = Marginal_Tax_Rate
        self.Capital_Gains_Tax = Capital_Gains_Tax
        self.Retired_Marginal_Tax_Rate = Retired_Marginal_Tax_Rate
        self.Retired_Capital_Gains_Tax = Retired_Capital_Gains_Tax

    
    def possible_starting_years(self):
        """ 
        Returns a list of possible starting years based on the start and end date of the historical data and the time window selected.
        """
        start_year = 1871
        end_year = 2021
        num_models_possible = (end_year-self.time_window)-start_year+2 # Have to add 2 to be inclusive of the end and start year 

        starting_years_list = []
        for i in range(num_models_possible):
            starting_years_list.append(start_year)
            start_year += 1
        return starting_years_list

    def Monte_Carlo_Plot_Spending(self, yearly_market_df):
        """ 
        Calls the model_account_returns_with_spending function for each possible starting year and appends the net and liquid asset pandas series to a DataFrame to be returned.
        
        # Parameters:
            yearly_market_df : pandas DataFrame object, default None
                pandas DataFrame that is passed to the model_account_returns_with_spending function as it contains the yearly market returns.
                
        # Returns:
            total_net_assets_df : pandas DataFrame object, default None
                pandas DataFrame that contains all the possible Monte Carlo simulated models of net assets for all possible time intervals.
            total_liquid_assets_df : pandas DataFrame object, default None
                pandas DataFrame that contains all the possible Monte Carlo simulated models of liquid assets for all possible time intervals.
        """
        total_liquid_assets_df = pd.DataFrame()
        total_net_assets_df = pd.DataFrame()
        for starting_year in self.possible_starting_years():
            # Need to create new dict with inital variables as these get changed and updated as model runs for each possible starting year.
            inital_balance_dict = {'balance_brokerage':self.balance_brokerage, 'balance_HSA':self.balance_HSA, 'balance_401k':self.balance_401k, 'balance_roth':self.balance_roth, 'balance_HSA_qualified_expense':self.balance_HSA_qualified_expense, 'balance_401k_contributions':self.balance_401k_contributions}

            Total_Net_Return_Spending, Total_Liquid_Return_Spending = self.model_account_returns_with_spending(inital_balance_dict, starting_year, yearly_market_df)

            total_liquid_assets_df = total_liquid_assets_df.append(Total_Liquid_Return_Spending)
            total_net_assets_df = total_net_assets_df.append(Total_Net_Return_Spending)

        return total_net_assets_df, total_liquid_assets_df

    def model_account_returns_with_spending(self, inital_balance_dict, starting_year, yearly_market_df):
        """ 
        Calculates the return of all investment accounts over the time window including yearly deposits and retirement spending.
        
        # Parameters:
            inital_balance_dict : dict, default None
                dictonary containing the inital account balances and the 
            starting_year : int, default None
                Integer value for the starting year to calculate the time frame to use for the return calculation. Between 1871 and 2021.
            yearly_market_df : pandas DataFrame object, default None
                pandas DataFrame that contains the yearly market returns used to model the account returns over the calculated time frame.
                
        # Returns:
            total_net_assets_df : pandas DataFrame object, default None
                pandas DataFrame that contains all the possible Monte Carlo simulated models of net assets for all possible time intervals.
            total_liquid_assets_df : pandas DataFrame object, default None
                pandas DataFrame that contains all the possible Monte Carlo simulated models of liquid assets for all possible time intervals.
        """
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        savings_remainder = self.yearly_savings
        ### DEPOSITS
        ### Calcuating HSA Contribution
        if self.yearly_savings//self.HSA_contribution_limit == 0:
            HSA_contribution = self.yearly_savings
            savings_remainder = 0
        else:
            HSA_contribution = self.HSA_contribution_limit
            savings_remainder -= self.HSA_contribution_limit

        ### Calcuating Roth Contribution
        # Have to calculate if savings is enough to fund Roth_contribution_limit (which is in after-tax dollars) with before-tax dollars.
        if savings_remainder*(1-self.Marginal_Tax_Rate/100)//self.Roth_contribution_limit == 0:
            # If (after-tax) savings_remainder is less than Roth_contribution_limit
            # Set Roth_contribution to be equal to all of the savings_remainder minus tax.
            # Roth is after tax dollars for contribution, so needs to be taxed before being added to account.
            Roth_contribution = savings_remainder*(1-self.Marginal_Tax_Rate/100)
            savings_remainder = 0
        else:
            # If after-tax savings_remainder is larger than Roth_contribution_limit, fully fund roth.
            # Remove Roth_contribution_limit plus tax from savings_remainder
            Roth_contribution = self.Roth_contribution_limit
            savings_remainder -= (self.Roth_contribution_limit/(1-self.Marginal_Tax_Rate/100))

        ### Calcuating 401k Contribution
        if savings_remainder//self.Traditional_401k_contribution_limit == 0:
            Traditional_401k_contribution = savings_remainder
            savings_remainder = 0
        else:
            Traditional_401k_contribution = self.Traditional_401k_contribution_limit
            savings_remainder -= self.Traditional_401k_contribution_limit

        ### Calcuating Brokerage Contribution
        Brokerage_contribution = savings_remainder*(1-self.Marginal_Tax_Rate/100)


        Brokerage_balance_over_time = []
        HSA_balance_over_time = []
        Trad_401k_balance_over_time = []
        Roth_balance_over_time = []

        Total_balance_over_time = []
        Total_Liquid_balance_over_time = []
        
        
        for i, percent in enumerate(model_return_data):
            # Stop adding yearly_savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 

            Brokerage_YB = inital_balance_dict['balance_brokerage']

            ### Calcuating Withdrawls
            # Withdraw Order Strategy: Brokerage Accounts --> HSA --> Traditonal 401k --> Roth

            withdraw_remainder = 0
            if i >= self.retirement_age-self.age:
                # After Retirement there are no more contributions but account values still change based on market returns and expense ratio fees.

                inital_balance_dict['balance_brokerage'] = inital_balance_dict['balance_brokerage']*(1+percent/100)
                inital_balance_dict['balance_brokerage'] = inital_balance_dict['balance_brokerage']*(1-self.Expense_Ratio/100)

                inital_balance_dict['balance_HSA'] = inital_balance_dict['balance_HSA']*(1+percent/100)
                inital_balance_dict['balance_HSA'] = inital_balance_dict['balance_HSA']*(1-self.Expense_Ratio/100)

                inital_balance_dict['balance_401k'] = inital_balance_dict['balance_401k']*(1+percent/100)
                inital_balance_dict['balance_401k'] = inital_balance_dict['balance_401k']*(1-self.Expense_Ratio/100)

                inital_balance_dict['balance_roth'] = inital_balance_dict['balance_roth']*(1+percent/100)
                inital_balance_dict['balance_roth'] = inital_balance_dict['balance_roth']*(1-self.Expense_Ratio/100)

                # Add the rolling balances to the balance_HSA_qualified_expense for the liquid plot calculation.
                inital_balance_dict['balance_HSA_qualified_expense'] = inital_balance_dict['balance_HSA_qualified_expense']+self.yearly_HSA_qualified_expense

                Brokerage_Capital_Gains = inital_balance_dict['balance_brokerage'] - Brokerage_YB
                if Brokerage_Capital_Gains < 0:
                    Brokerage_Capital_Gains = 0
                
                # Remove the Captial Gains Tax from Brokerage Account.
                inital_balance_dict['balance_brokerage'] = inital_balance_dict['balance_brokerage'] - Brokerage_Capital_Gains*(self.Capital_Gains_Tax/100)

                # Remove retirement spend from Brokerage account first.
                inital_balance_dict['balance_brokerage'] = inital_balance_dict['balance_brokerage']-self.retirement_spend
                if inital_balance_dict['balance_brokerage'] < 0:
                    withdraw_remainder = abs(inital_balance_dict['balance_brokerage'])
                    inital_balance_dict['balance_brokerage'] = 0

                # Remove retirement spend from HSA account next.
                inital_balance_dict['balance_HSA'] = inital_balance_dict['balance_HSA']-withdraw_remainder
                # Remove remainder also for balance_HSA_qualified_expense account to track liquid spend potential.
                inital_balance_dict['balance_HSA_qualified_expense'] = inital_balance_dict['balance_HSA_qualified_expense']-withdraw_remainder
                # Set HSA balance to zero if the withdraw amount was larger than the account balance
                if inital_balance_dict['balance_HSA'] < 0:
                    inital_balance_dict['balance_HSA'] = 0
                    
                # Set HSA qualified expense balance to zero if the withdraw amount was larger than the account balance
                # This remainder is what is sent to the other accounts, as it is realistically the the only valid funds that can be removed.
                if inital_balance_dict['balance_HSA_qualified_expense'] < 0:
                    withdraw_remainder = abs(inital_balance_dict['balance_HSA_qualified_expense'])
                    inital_balance_dict['balance_HSA_qualified_expense'] = 0
                else:
                    withdraw_remainder = 0

                if i+self.age+1 > 59:

                    # Remove retirement spend from Tradtional 401k account next.
                    # Remove the withdraw_remainder plus the income tax owed for that withdraw from the 401k account.
                    inital_balance_dict['balance_401k'] = inital_balance_dict['balance_401k']-((withdraw_remainder*(1+self.Retired_Marginal_Tax_Rate/100)))
                    if inital_balance_dict['balance_401k'] < 0:
                        withdraw_remainder = abs(inital_balance_dict['balance_401k'])
                        inital_balance_dict['balance_401k'] = 0

                    # Remove retirement spend from Roth account last.
                    inital_balance_dict['balance_roth'] = inital_balance_dict['balance_roth']-(withdraw_remainder)
                    if inital_balance_dict['balance_roth'] < 0:
                        withdraw_remainder = abs(inital_balance_dict['balance_roth'])
                        inital_balance_dict['balance_roth'] = 0             
                
                # If there is still a withdraw remainder then both the HSA liquid balance, and Brokerage account balance are 0 before money is availbile from your other accounts.
                if withdraw_remainder > 0:
                    pass

            else:
                # Before Retirement calculate the market return and remove the expense ratio fee for each account.
                inital_balance_dict['balance_brokerage'] = (inital_balance_dict['balance_brokerage']+Brokerage_contribution)*(1+percent/100)
                inital_balance_dict['balance_brokerage'] = inital_balance_dict['balance_brokerage']*(1-self.Expense_Ratio/100)

                inital_balance_dict['balance_HSA'] = (inital_balance_dict['balance_HSA']+HSA_contribution)*(1+percent/100)
                inital_balance_dict['balance_HSA'] = inital_balance_dict['balance_HSA']*(1-self.Expense_Ratio/100)

                inital_balance_dict['balance_401k'] = (inital_balance_dict['balance_401k']+Traditional_401k_contribution)*(1+percent/100)
                inital_balance_dict['balance_401k'] = inital_balance_dict['balance_401k']*(1-self.Expense_Ratio/100)

                inital_balance_dict['balance_roth'] = (inital_balance_dict['balance_roth']+Roth_contribution)*(1+percent/100)
                inital_balance_dict['balance_roth'] = inital_balance_dict['balance_roth']*(1-self.Expense_Ratio/100)

                # Add the rolling balances to the balance_HSA_qualified_expense and balance_401k_contributions accounts for the liquid plot calculation.
                inital_balance_dict['balance_HSA_qualified_expense'] = inital_balance_dict['balance_HSA_qualified_expense']+self.yearly_HSA_qualified_expense
                inital_balance_dict['balance_401k_contributions'] = inital_balance_dict['balance_401k_contributions']+Traditional_401k_contribution

                # Removing the Capital Gains Tax in Brokerage Account
                Brokerage_Capital_Gains = inital_balance_dict['balance_brokerage'] - Brokerage_YB
                
                if Brokerage_Capital_Gains < 0:
                    Brokerage_Capital_Gains = 0

                inital_balance_dict['balance_brokerage'] = inital_balance_dict['balance_brokerage'] - Brokerage_Capital_Gains*(self.Capital_Gains_Tax/100) # Remove the Captial Gains Tax


            total_balance = inital_balance_dict['balance_brokerage'] + inital_balance_dict['balance_HSA'] + inital_balance_dict['balance_401k'] + inital_balance_dict['balance_roth']

            if i+self.age+1 > 59:
                total_liquid_balance = inital_balance_dict['balance_brokerage'] + inital_balance_dict['balance_HSA_qualified_expense'] + inital_balance_dict['balance_401k'] + inital_balance_dict['balance_roth']
            else:
                total_liquid_balance = inital_balance_dict['balance_brokerage'] + inital_balance_dict['balance_HSA_qualified_expense']

            Brokerage_balance_over_time.append(inital_balance_dict['balance_brokerage'])
            HSA_balance_over_time.append(inital_balance_dict['balance_HSA'])
            Trad_401k_balance_over_time.append(inital_balance_dict['balance_401k'])
            Roth_balance_over_time.append(inital_balance_dict['balance_roth'])

            Total_balance_over_time.append(total_balance)
            Total_Liquid_balance_over_time.append(total_liquid_balance)

        Total_Net_Return_Spending = pd.Series(Total_balance_over_time, index=year_range, name=starting_year)
        Total_Liquid_Return_Spending = pd.Series(Total_Liquid_balance_over_time, index=year_range, name=starting_year)
        
        return Total_Net_Return_Spending, Total_Liquid_Return_Spending

    def model_brokerage_returns(self, yearly_market_df, starting_year):
        """ 
        Calculates the net and liquid returns of a brokerage account from a specific historical starting year including yearly deposits.
        Does not include retirement spend and is used for the account value comparison plot.
        
        # Parameters:
            yearly_market_df : pandas DataFrame object, default None
                pandas DataFrame that contains the yearly market returns used to model the account returns over the calculated time frame.
            starting_year : int, default None
                Integer value for the starting year to calculate the time frame to use for the return calculation. Between 1871 and 2021.
                
        # Returns:
            net_return : pandas Series object, default None
                pandas Series that contains the net brokerage account values for this historic model.
            liquid_balance : pandas Series object, default None
                pandas Series that contains the liquid brokerage account values for this historic model.
        """ 
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        after_tax_yearly_investment = self.yearly_savings*(1-self.Marginal_Tax_Rate/100)
        YB_balance = self.growth_comparison_starting_balance
        deposit_balance = self.growth_comparison_starting_balance
        liquid_balance = self.growth_comparison_starting_balance

        ### Brokerage Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []
        for i, percent in enumerate(model_return_data): 
            # Stop adding yearly_savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
                # Calculate the dollars gained each year that would need to be taxed as capital gains. Assumes yearly selling and reinvestment of gains (conservative assumption)
                Brokerage_Capital_Gains = YE_balance - (YB_balance)
            else:
                deposit_balance = deposit_balance+after_tax_yearly_investment
                YE_balance = (YB_balance+after_tax_yearly_investment)*(1+percent/100)
                # Calculate the dollars gained each year that would need to be taxed as capital gains. Assumes yearly selling and reinvestment of gains (conservative assumption)
                Brokerage_Capital_Gains = YE_balance - (YB_balance+after_tax_yearly_investment)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance

            if Brokerage_Capital_Gains < 0:
                Brokerage_Capital_Gains = 0

            YE_balance = YE_balance - Brokerage_Capital_Gains*(self.Capital_Gains_Tax/100) # Remove the Captial Gains Tax
            YE_balance = YE_balance*(1-self.Expense_Ratio/100) # Remove expense ratio from YE balance
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance
            # Append balance of liquid assets (100% of assets after tax)
            liquid_balance = YE_balance
            liquid_balance_over_time.append(liquid_balance)
    
        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance

    def model_HSA_returns(self, yearly_market_df, starting_year):
        """ 
        Calculates the net and liquid returns of a HSA account from a specific historical starting year including yearly deposits.
        Does not include retirement spend and is used for the account value comparison plot.
        
        # Parameters:
            yearly_market_df : pandas DataFrame object, default None
                pandas DataFrame that contains the yearly market returns used to model the account returns over the calculated time frame.
            starting_year : int, default None
                Integer value for the starting year to calculate the time frame to use for the return calculation. Between 1871 and 2021.
                
        # Returns:
            net_return : pandas Series object, default None
                pandas Series that contains the net HSA account values for this historic model.
            liquid_balance : pandas Series object, default None
                pandas Series that contains the liquid HSA account values for this historic model.
        """ 
        # 2022 deposit limit is $3600. Model assumes this is added in total at start of year
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()
        year_range = list(np.arange(1,self.time_window+1))

        YB_balance = self.growth_comparison_starting_balance # Year Begin balance. Starts with just the beginning account value
        liquid_balance = 0
        deposit_balance = self.growth_comparison_starting_balance

        ### HSA Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []

        for i, percent in enumerate(model_return_data):
            # Stop adding yearly_savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
            else:
                deposit_balance = deposit_balance+self.yearly_savings
                YE_balance = (YB_balance+self.yearly_savings)*(1+percent/100)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance


            YE_balance = YE_balance*(1-self.Expense_Ratio/100)
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance
            liquid_balance = liquid_balance+self.yearly_HSA_qualified_expense
            liquid_balance_over_time.append(liquid_balance)

        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance

    def model_roth_returns(self, yearly_market_df, starting_year):
        """ 
        Calculates the net and liquid returns of a Roth account from a specific historical starting year including yearly deposits.
        Does not include retirement spend and is used for the account value comparison plot.
        
        # Parameters:
            yearly_market_df : pandas DataFrame object, default None
                pandas DataFrame that contains the yearly market returns used to model the account returns over the calculated time frame.
            starting_year : int, default None
                Integer value for the starting year to calculate the time frame to use for the return calculation. Between 1871 and 2021.
                
        # Returns:
            net_return : pandas Series object, default None
                pandas Series that contains the net ROth account values for this historic model.
            liquid_balance : pandas Series object, default None
                pandas Series that contains the liquid Roth account values for this historic model.
        """ 
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        after_tax_yearly_investment = self.yearly_savings*(1-self.Marginal_Tax_Rate/100) # Roth Contributions are paid with after tax dollars
        YB_balance = self.growth_comparison_starting_balance # Year Begin balance. Starts with just the beginning account value
        liquid_balance = 0
        deposit_balance = self.growth_comparison_starting_balance

        ### 401k Roth Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []
        
        for i, percent in enumerate(model_return_data):
            # Stop adding after_tax_yearly_investment if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
            else:
                deposit_balance = deposit_balance+after_tax_yearly_investment
                YE_balance = (YB_balance+after_tax_yearly_investment)*(1+percent/100)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance

            YE_balance = YE_balance*(1-self.Expense_Ratio/100)
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance

            if i+self.age+1 > 59:
                liquid_balance = YE_balance

            liquid_balance_over_time.append(liquid_balance)

        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance

    def model_trad_401k_returns(self, yearly_market_df, starting_year):
        """ 
        Calculates the net and liquid returns of a Traditional 401k account from a specific historical starting year including yearly deposits.
        Does not include retirement spend and is used for the account value comparison plot.
        
        # Parameters:
            yearly_market_df : pandas DataFrame object, default None
                pandas DataFrame that contains the yearly market returns used to model the account returns over the calculated time frame.
            starting_year : int, default None
                Integer value for the starting year to calculate the time frame to use for the return calculation. Between 1871 and 2021.
                
        # Returns:
            net_return : pandas Series object, default None
                pandas Series that contains the net Traditional 401k account values for this historic model.
            liquid_balance : pandas Series object, default None
                pandas Series that contains the liquid Traditional 401k account values for this historic model.
        """ 
        # Create a copy of just the relevant years of Real_Return_Percentage based on the time range and the starting year
        model_return_data = yearly_market_df.loc[starting_year:starting_year+self.time_window-1, 'Real_Return_Percentage'].copy()

        year_range = list(np.arange(1,self.time_window+1))

        YB_balance = self.growth_comparison_starting_balance # Year Begin balance. Starts with just the beginning account value
        liquid_balance = 0
        deposit_balance = self.growth_comparison_starting_balance

        ### 401k Account
        balance_over_time = []
        deposit_balance_over_time = []
        liquid_balance_over_time = []

        for i, percent in enumerate(model_return_data):
            # Stop adding yearly_savings if past retirement age
            # model_return_data corresponds with age of user. i.e. model_return_data[0] == age, model_return_data[1] == age+1 
            if i >= self.retirement_age-self.age:
                deposit_balance = deposit_balance
                YE_balance = (YB_balance)*(1+percent/100)
            else:
                deposit_balance = deposit_balance+self.yearly_savings
                YE_balance = (YB_balance+self.yearly_savings)*(1+percent/100)

            deposit_balance_over_time.append(deposit_balance) # Keep track of contribution balance

            YE_balance = YE_balance*(1-self.Expense_Ratio/100)
            balance_over_time.append(YE_balance)
            YB_balance = YE_balance

            # Assets are not liquid until after user turns over 59 years old in a 401k account
            # Assets are then taxed as income at the now retired persons tax rates
            if i+self.age+1 > 59:
                liquid_capital_gains = (YE_balance-deposit_balance)*(1-self.Retired_Capital_Gains_Tax/100)
                liquid_deposits = deposit_balance*(1-self.Retired_Marginal_Tax_Rate/100)
                liquid_balance = liquid_capital_gains+liquid_deposits


            liquid_balance_over_time.append(liquid_balance)

        net_return = pd.Series(balance_over_time, index=year_range, name=starting_year)
        liquid_balance = pd.Series(liquid_balance_over_time, index=year_range, name=starting_year)

        return net_return, liquid_balance

    def Monte_Carlo_Growth_Models(self, account_type, yearly_market_df):
        """ 
        Depending on the account type calls the correct modeling function for each of the possible starting years in the Monte Carlo comparison plot.
        
        # Parameters:
            account_type : str, default None
                String for the name of the account type to use for the Monte Carlo calculation. Has to be one of the following ['HSA', 'Roth', 'Trade_401k', 'Brokerage']
            yearly_market_df : pandas DataFrame object, default None
                pandas DataFrame that contains the yearly market returns used to model the account returns over the calculated time frame.
                
        # Returns:
            df : pandas DataFrame object, default None
                pandas DataFrame that contains the net modeled account values all possible years for the specified account.
            liquid_df : pandas DataFrame object, default None
                pandas DataFrame that contains the liquid modeled account values all possible years for the specified account.
        """ 
        ### Model all the possible returns for every possible time window
        df = pd.DataFrame()
        liquid_df = pd.DataFrame()

        if account_type == 'HSA':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_HSA_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
            
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.HSA_models_df = df
            self.HSA_models_liquid_df = liquid_df
            
        elif account_type == 'Roth':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_roth_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
                
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.Roth_models_df = df
            self.Roth_models_liquid_df = liquid_df
            
        elif account_type == 'Trad_401k':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_trad_401k_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
                
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.Trad_401k_models_df = df
            self.Trad_401k_models_liquid_df = liquid_df
            
        elif account_type == 'Brokerage':
            for starting_year in self.possible_starting_years():
                net_return, liquid_balance = self.model_brokerage_returns(yearly_market_df, starting_year)
                # plt.plot(net_return, color=global_color_scheme[color_alt])
                df = df.append(net_return)
                liquid_df = liquid_df.append(liquid_balance)
                
            # Transpose DataFrames for easier plotting
            df = df.T
            liquid_df = liquid_df.T
            # Save DataFrames as objects associated with Class object
            self.Brokerage_models_df = df
            self.Brokerage_models_liquid_df = liquid_df
            
        else:
            raise ValueError('Account type parameter was not one of following strings in list: ["HSA", "Roth", "Trad_401k", "Brokerage"]')

        return df, liquid_df

    def cash_balance(self):
        """ 
        Returns a DataFrame that shows the after tax cash investment of the yearly savings (which is pre-tax). 
        Used in the comparison plot from the Monte_Carlo_Plot_Growth_Comparison function to show just deposits over time. 
        """ 
        # Cash investment, showing just yearly savings
        # Cash Contributions are also made after tax. Yearly Savings in based of a Gross number
        after_tax_yearly_investment = self.yearly_savings*(1-self.Marginal_Tax_Rate/100)
        # years where you would still make cash deposits
        years_until_retirement = self.retirement_age-self.age
        deposits_before_retirement = np.arange(start=after_tax_yearly_investment, stop=after_tax_yearly_investment*(years_until_retirement+1), step=after_tax_yearly_investment)
        if len(deposits_before_retirement) >= self.time_window:
            deposit_balance = deposits_before_retirement[0:self.time_window]
        else:
            deposit_balance = np.concatenate([deposits_before_retirement, np.full(self.time_window-len(deposits_before_retirement), deposits_before_retirement[-1])])

        plot_index = np.arange(1,self.time_window+1)
        
        cash_balance_df = pd.DataFrame(deposit_balance,plot_index)
        return cash_balance_df